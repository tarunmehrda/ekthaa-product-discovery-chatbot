import os
from groq import Groq

def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("Missing GROQ_API_KEY in environment")
    return Groq(api_key=api_key)

def llm_extract(message: str) -> dict:
    """
    Ask Groq to convert user query into structured filters.
    """
    client = get_groq_client()

    system = """
You are an NLU engine for a product discovery chatbot.
Extract intent + filters from user message and return ONLY valid JSON.

Supported intents:
- product_search
- price_filter
- category_search
- business_finder
- no_result

Return JSON keys:
{
  "intent": "...",
  "product_name": "string or null",
  "category": "Grocery/Vegetables or null",
  "max_price": number or null,
  "business_category": "Grocery/Vegetables or null"
}

Rules:
- If query mentions "under", "below", "less than", set max_price
- If query is like "where can I buy vegetables" => category_search
- If query says "grocery stores near me" => business_finder + business_category="Grocery"
- If query asks "who sells dal" => product_search, product_name="dal"
    """

    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": message}
        ],
        temperature=0.1,
        max_tokens=300
    )

    text = resp.choices[0].message.content.strip()

    # Small safety cleanup
    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    import json
    return json.loads(text)

def llm_fallback_response(user_message: str, detected_intent: dict | None = None) -> str:
    """
    Generate a friendly conversational response when no database results are found.
    """
    client = get_groq_client()

    system = """
You are a helpful product discovery assistant for local stores in Hyderabad.
You have access to a small catalog of grocery and vegetable items.
If the user asks for something not in the catalog, respond politely and suggest what you *do* have.
Keep responses short and conversational.
"""

    context = ""
    if detected_intent:
        parts = []
        if detected_intent.get("product_name"):
            parts.append(f"they were looking for: {detected_intent['product_name']}")
        if detected_intent.get("category"):
            parts.append(f"category: {detected_intent['category']}")
        if detected_intent.get("max_price"):
            parts.append(f"budget: under Rs.{detected_intent['max_price']}")
        if parts:
            context = "Detected intent: " + "; ".join(parts) + "."

    user_prompt = f"User said: \"{user_message}\". {context} Respond helpfully."

    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=200
    )

    return resp.choices[0].message.content.strip()

def llm_suggest_questions() -> list[str]:
    """
    Generate a list of example questions the user can ask, based on the catalog.
    """
    client = get_groq_client()

    system = """
You are a product discovery assistant for local stores in Hyderabad.
The catalog includes:
- Products: Basmati Rice, Fresh Tomatoes, Sunflower Oil, Whole Wheat Atta, Fresh Onions, Toor Dal
- Categories: Grocery, Vegetables
- Businesses: Sai Kirana Store (Madhapur), Fresh Mart Vegetables (Gachibowli), Quality Grocers (Kondapur)

Generate 4–6 short, natural example questions a user might ask.
Return ONLY a JSON list of strings, e.g.:
["Show me rice", "Products under Rs.50", "Where can I buy vegetables?", "Grocery stores near me", "Who sells dal?", "Do you have apples?"]
"""

    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": "Suggest example questions for the chatbot."}
        ],
        temperature=0.5,
        max_tokens=250
    )

    text = resp.choices[0].message.content.strip()
    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    import json
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Fallback static list
        return [
            "Show me rice",
            "Products under Rs.50",
            "Where can I buy vegetables?",
            "Grocery stores near me",
            "Who sells dal?",
            "Do you have apples?"
        ]
