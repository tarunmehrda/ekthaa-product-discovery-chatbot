def format_products(products):
    lines = []
    for i, p in enumerate(products, start=1):
        lines.append(f"{i}. {p['name']} - Rs.{p['price']}/{p['unit']}\n{p['business_name']}, {p['business_address']}\nPhone: {p['business_phone']}")
    return "\n\n".join(lines)

def format_businesses(businesses):
    lines = []
    for i, b in enumerate(businesses, start=1):
        prod_names = ", ".join(b["products"])
        lines.append(f"{i}. {b['name']} - {b['address']}\nProducts: {prod_names}\nPhone: {b['phone']}")
    return "\n\n".join(lines)
