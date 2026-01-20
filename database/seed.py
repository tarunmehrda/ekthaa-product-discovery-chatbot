import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "ekthaa.db")

products = [
    {"id":"1","name":"Basmati Rice","price":120,"unit":"kg","category":"Grocery","business_id":"b1"},
    {"id":"2","name":"Fresh Tomatoes","price":40,"unit":"kg","category":"Vegetables","business_id":"b2"},
    {"id":"3","name":"Sunflower Oil","price":180,"unit":"liter","category":"Grocery","business_id":"b1"},
    {"id":"4","name":"Whole Wheat Atta","price":50,"unit":"kg","category":"Grocery","business_id":"b3"},
    {"id":"5","name":"Fresh Onions","price":35,"unit":"kg","category":"Vegetables","business_id":"b2"},
    {"id":"6","name":"Toor Dal","price":140,"unit":"kg","category":"Grocery","business_id":"b3"},
]

businesses = [
    {"id":"b1","name":"Sai Kirana Store","category":"Grocery","address":"Madhapur, Hyderabad","phone":"9876543210"},
    {"id":"b2","name":"Fresh Mart Vegetables","category":"Vegetables","address":"Gachibowli, Hyderabad","phone":"9876543211"},
    {"id":"b3","name":"Quality Grocers","category":"Grocery","address":"Kondapur, Hyderabad","phone":"9876543212"},
]

def main():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS businesses (
        id TEXT PRIMARY KEY,
        name TEXT,
        category TEXT,
        address TEXT,
        phone TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id TEXT PRIMARY KEY,
        name TEXT,
        price INTEGER,
        unit TEXT,
        category TEXT,
        business_id TEXT,
        FOREIGN KEY (business_id) REFERENCES businesses(id)
    )
    """)

    cur.execute("DELETE FROM products")
    cur.execute("DELETE FROM businesses")

    for b in businesses:
        cur.execute("INSERT INTO businesses VALUES (?, ?, ?, ?, ?)",
                    (b["id"], b["name"], b["category"], b["address"], b["phone"]))

    for p in products:
        cur.execute("INSERT INTO products VALUES (?, ?, ?, ?, ?, ?)",
                    (p["id"], p["name"], p["price"], p["unit"], p["category"], p["business_id"]))

    conn.commit()
    conn.close()
    print("✅ Database seeded successfully:", DB_PATH)

if __name__ == "__main__":
    main()
