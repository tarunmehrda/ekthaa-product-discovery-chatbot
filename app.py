import os
import sqlite3
import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from utils.groq_client import llm_extract, llm_fallback_response, llm_suggest_questions
from utils.query_parser import fuzzy_product_match, fuzzy_category_match
from utils.response_formatter import format_products, format_businesses
from utils.memory import get_context, update_context

load_dotenv()

app = FastAPI(title="Ekthaa Product Discovery Chatbot")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

DB_PATH = os.path.join("database", "ekthaa.db")

class ChatRequest(BaseModel):
    message: str
    user_id: str | None = None
    location: dict | None = None  # optional

def db_conn():
    return sqlite3.connect(DB_PATH)

def _locality(address: str | None) -> str:
    if not address:
        return ""
    return address.split(",")[0].strip()

def _serialize_products(products: list[dict]) -> list[dict]:
    out = []
    for p in products:
        out.append(
            {
                "id": p.get("id"),
                "name": p.get("name"),
                "price": p.get("price"),
                "unit": p.get("unit"),
                "category": p.get("category"),
                "business_id": p.get("business_id"),
                "business": {
                    "name": p.get("business_name"),
                    "address": p.get("business_address"),
                    "phone": p.get("business_phone"),
                },
            }
        )
    return out

def _heuristic_extract(message: str) -> dict:
    m = message.lower()

    max_price = None
    price_match = re.search(r"(?:under|below|less\s+than)\s*(?:rs\.?|₹)?\s*(\d+)", m)
    if price_match:
        max_price = int(price_match.group(1))

    category = None
    if "vegetable" in m or "veggies" in m:
        category = "Vegetables"
    elif "grocery" in m:
        category = "Grocery"

    product_name = None
    if " rice" in f" {m} " or m.endswith("rice"):
        product_name = "rice"
    elif " dal" in f" {m} " or m.endswith("dal"):
        product_name = "dal"
    else:
        generic = re.search(r"(?:show\s+me|find|search\s+for|do\s+you\s+have)\s+([a-z\s]+)", m)
        if generic:
            product_name = generic.group(1).strip().split()[0]

    intent = None
    if ("store" in m or "stores" in m or "shop" in m or "shops" in m) and ("near me" in m or "nearby" in m):
        intent = "business_finder"
    elif category and ("where can i buy" in m or "where to buy" in m or "where" in m and "buy" in m):
        intent = "category_search"
    elif max_price is not None and not product_name:
        intent = "price_filter"
    elif product_name:
        intent = "product_search"

    return {
        "intent": intent,
        "product_name": product_name,
        "category": category,
        "max_price": max_price,
        "business_category": category if intent == "business_finder" else None,
    }

def fetch_products(product_name=None, category=None, max_price=None):
    conn = db_conn()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = """
    SELECT p.*, b.name as business_name, b.address as business_address, b.phone as business_phone
    FROM products p
    JOIN businesses b ON p.business_id = b.id
    WHERE 1=1
    """
    params = []

    if product_name:
        query += " AND LOWER(p.name) LIKE ?"
        params.append(f"%{product_name.lower()}%")

    if category:
        query += " AND LOWER(p.category) = ?"
        params.append(category.lower())

    if max_price is not None:
        query += " AND p.price <= ?"
        params.append(int(max_price))

    cur.execute(query, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def fetch_businesses(business_category=None):
    conn = db_conn()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = "SELECT * FROM businesses WHERE 1=1"
    params = []
    if business_category:
        query += " AND LOWER(category)=?"
        params.append(business_category.lower())

    cur.execute(query, params)
    businesses = [dict(r) for r in cur.fetchall()]

    # attach products
    for b in businesses:
        cur.execute("SELECT name FROM products WHERE business_id=?", (b["id"],))
        b["products"] = [x[0] for x in cur.fetchall()]

    conn.close()
    return businesses

def suggest_similar(category=None):
    # Basic suggestion fallback
    if category:
        return fetch_products(category=category)
    return fetch_products(category="Vegetables")

@app.post("/chat")
def chat(req: ChatRequest):
    msg = req.message.strip()
    user_id = req.user_id or "anonymous"

    # LLM extraction
    try:
        parsed = llm_extract(msg)
    except Exception:
        parsed = _heuristic_extract(msg)

    # Context support (followups)
    context = get_context(user_id)
    parsed = {
        "intent": parsed.get("intent") or context.get("intent"),
        "product_name": parsed.get("product_name") or context.get("product_name"),
        "category": parsed.get("category") or context.get("category"),
        "max_price": parsed.get("max_price") if parsed.get("max_price") is not None else context.get("max_price"),
        "business_category": parsed.get("business_category") or context.get("business_category"),
    }
    update_context(user_id, parsed)

    intent = parsed["intent"]

    # --- Intent Handling ---
    if intent in ["product_search", "price_filter"]:
        # typo handling: product name
        if parsed["product_name"]:
            corrected = fuzzy_product_match(parsed["product_name"])
            if corrected:
                parsed["product_name"] = corrected

        if parsed["category"]:
            corrected_cat = fuzzy_category_match(parsed["category"])
            if corrected_cat:
                parsed["category"] = corrected_cat

        prods = fetch_products(
            product_name=parsed["product_name"],
            category=parsed["category"],
            max_price=parsed["max_price"]
        )

        if not prods:
            try:
                fallback = llm_fallback_response(msg, detected_intent=parsed)
            except Exception:
                # Ultra-safe fallback if Groq fails
                suggestion_cat = parsed.get("category")
                suggestion_prompt = "products"
                if suggestion_cat:
                    suggestion_prompt = suggestion_cat.lower()
                    suggestion_prompt_text = f"Would you like to see all available {suggestion_prompt}?"
                else:
                    suggestion_prompt_text = "Would you like to see all available products?"
                fallback = f"Sorry, I couldn't find {parsed.get('product_name') or 'that'} in our database.\n{suggestion_prompt_text}"

            return {
                "response": fallback,
                "products": [],
                "intent": "no_result"
            }

        m_lower = msg.lower()
        if parsed.get("max_price") is not None and not parsed.get("product_name") and not parsed.get("category"):
            header = f"Found {len(prods)} products under Rs.{int(parsed['max_price'])}:\n"
            lines = []
            for i, p in enumerate(prods, start=1):
                lines.append(
                    f"{i}. {p['name']} - Rs.{p['price']}/{p['unit']}\n{p['business_name']}, {_locality(p['business_address'])}"
                )
            return {
                "response": header + "\n".join(lines),
                "products": _serialize_products(prods),
                "intent": intent,
            }

        if len(prods) == 1:
            p = prods[0]
            if "who sells" in m_lower or "who sell" in m_lower:
                resp = (
                    f"{p['name']} is available at:\n"
                    f"{p['name']} - Rs.{p['price']}/{p['unit']}\n"
                    f"{p['business_name']}\n"
                    f"{p['business_address']}\n"
                    f"Phone: {p['business_phone']}"
                )
            else:
                resp = (
                    "Found 1 product:\n"
                    f"{p['name']} - Rs.{p['price']}/{p['unit']}\n"
                    f"Available at: {p['business_name']}, {_locality(p['business_address'])}\n"
                    f"Call: {p['business_phone']}"
                )
            return {
                "response": resp,
                "products": _serialize_products(prods),
                "intent": intent,
            }

        header = f"Found {len(prods)} products:\n\n"
        lines = []
        for i, p in enumerate(prods, start=1):
            lines.append(
                f"{i}. {p['name']} - Rs.{p['price']}/{p['unit']}\n{p['business_name']}, {_locality(p['business_address'])}\nPhone: {p['business_phone']}"
            )
        return {
            "response": header + "\n\n".join(lines),
            "products": _serialize_products(prods),
            "intent": intent,
        }

    if intent == "category_search":
        # category fuzzy match
        if parsed["category"]:
            corrected_cat = fuzzy_category_match(parsed["category"])
            if corrected_cat:
                parsed["category"] = corrected_cat

        if not parsed["category"]:
            parsed["category"] = "Vegetables"

        businesses = fetch_businesses(business_category=parsed["category"])
        if not businesses:
            return {"response": "No businesses found in this category.", "products": [], "intent": "no_result"}

        # pick first relevant business
        b = businesses[0]
        products = fetch_products(category=parsed["category"])

        resp = (
            f"{b['name']} in {_locality(b['address'])} specializes in {parsed['category'].lower()}.\n"
            f"Available products:\n"
        )
        for p in products:
            if p["business_name"] == b["name"]:
                resp += f"• {p['name']} - Rs.{p['price']}/{p['unit']}\n"
        resp += f"Address: {b['address']}\nPhone: {b['phone']}"

        return {
            "response": resp.strip(),
            "products": _serialize_products(products),
            "businesses": businesses,
            "intent": intent,
        }

    if intent == "business_finder":
        businesses = fetch_businesses(business_category=parsed["business_category"])
        if not businesses:
            businesses = fetch_businesses()  # fallback

        header = f"Found {len(businesses)} store(s):\n\n"
        if parsed.get("business_category"):
            header = f"Found {len(businesses)} {parsed['business_category'].lower()} stores:\n\n"

        lines = []
        for i, b in enumerate(businesses, start=1):
            prod_names = ", ".join(b.get("products", []))
            lines.append(
                f"{i}. {b['name']} - {_locality(b['address'])}\nProducts: {prod_names}\nPhone: {b['phone']}"
            )

        resp = header + "\n\n".join(lines)
        return {"response": resp, "products": [], "businesses": businesses, "intent": intent}

    # fallback
    return {
        "response": "I can help you find grocery/vegetable products. Try: 'Show me rice under 150' or 'Grocery stores near me'.",
        "products": [],
        "intent": "fallback"
    }

# Health check
@app.get("/")
def root():
    return {"status": "ok", "message": "Ekthaa Product Discovery Chatbot Running ✅"}

# Suggest example questions (Groq-powered)
@app.get("/suggest")
def suggest():
    try:
        questions = llm_suggest_questions()
        return {"questions": questions}
    except Exception as e:
        # Fallback static suggestions
        return {
            "questions": [
                "Show me rice",
                "Products under Rs.50",
                "Where can I buy vegetables?",
                "Grocery stores near me",
                "Who sells dal?",
                "Do you have apples?"
            ]
        }
