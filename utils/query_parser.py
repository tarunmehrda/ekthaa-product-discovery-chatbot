from rapidfuzz import process, fuzz

KNOWN_PRODUCTS = ["Basmati Rice", "Fresh Tomatoes", "Sunflower Oil", "Whole Wheat Atta", "Fresh Onions", "Toor Dal"]
KNOWN_CATEGORIES = ["Grocery", "Vegetables"]

def fuzzy_product_match(q: str):
    match = process.extractOne(q, KNOWN_PRODUCTS, scorer=fuzz.WRatio)
    if match and match[1] >= 70:
        return match[0]
    return None

def fuzzy_category_match(q: str):
    match = process.extractOne(q, KNOWN_CATEGORIES, scorer=fuzz.WRatio)
    if match and match[1] >= 70:
        return match[0]
    return None
