import random
import psycopg2
from faker import Faker
from decimal import Decimal
import settings


fake = Faker(['en_GB'])

conn = psycopg2.connect(
    dbname=settings.DB_NAME,
    user=settings.DB_USER,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
    port=settings.DB_PORT
)
cursor = conn.cursor()


def generate_email(first_name, last_name):
    return f"{first_name.lower()}.{last_name.lower()}@example.com"

def generate_phone_number():
    return f"+{random.randint(100, 999)} {random.randint(10, 99)} {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}"


def insert_customers(n=10):
    for i in range(1, n + 1):
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = generate_email(first_name, last_name)
        phone_number = generate_phone_number()
        registration_date = fake.date_time_between(start_date="-5y", end_date="-1y")
        last_login_date = fake.date_time_between(start_date=registration_date, end_date="now")
        
        cursor.execute(
            """INSERT INTO customers (customer_id, first_name, last_name, age, email, country, city, postal_code, phone_number, registration_date, last_login_date)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                i, first_name, last_name, random.randint(18, 70), email,
                fake.country(), fake.city(), fake.postcode(), phone_number,
                registration_date, last_login_date
            )
        )
    conn.commit()

def insert_orders(n=20):
    cursor.execute("SELECT customer_id FROM customers")
    customers = [row[0] for row in cursor.fetchall()]
    
    statuses = ['Pending', 'Shipped', 'Delivered', 'Cancelled']
    payment_methods = ['Credit Card', 'PayPal', 'Bank Transfer']
    
    for _ in range(n):
        cursor.execute(
            """INSERT INTO orders (customer_id, order_date, total_amount, status, shipping_address, payment_method, currency)
               VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING order_id""",
            (
                random.choice(customers), fake.date_time_this_decade(), round(random.uniform(10, 1000), 2),
                random.choice(statuses), fake.address(), random.choice(payment_methods), 'EUR'
            )
        )
    conn.commit()

def insert_suppliers(n=10):
    for _ in range(n):
        first_name = fake.first_name()
        last_name = fake.last_name()
        name = f"{first_name} {last_name}"
        email = generate_email(first_name, last_name)
        phone_number = generate_phone_number()
        
        cursor.execute(
            """INSERT INTO suppliers (company_name, contact_name, email, phone, country, lead_time)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (
                fake.company(), name, email, phone_number,
                fake.country(), random.randint(1, 14)
            )
        )
    conn.commit()

def insert_products(n=50):
    cursor.execute("SELECT supplier_id FROM suppliers")
    suppliers = [row[0] for row in cursor.fetchall()]
    
    categories = {
        "Electronics": ["Smartphone", "Laptop", "Camera", "Headphones"],
        "Clothing": ["T-Shirt", "Jeans", "Sneakers", "Jacket"],
        "Home": ["Sofa", "Table", "Chair", "Lamp"],
        "Toys": ["Action Figure", "Board Game", "Doll"],
        "Books": ["Fiction Novel", "Non-Fiction Book", "Comic Book"],
        "Beauty": ["Lipstick", "Skincare Cream", "Perfume"],
        "Sports": ["Running Shoes", "Basketball", "Yoga Mat"]
    }
    categories_list = list(categories.keys())

    for i in range(1, n + 1):
        category = random.choice(categories_list)
        subcategory = random.choice(categories[category])
        
        price = round(random.uniform(10, 500), 2)
        cost = round(random.uniform(5, price - 5), 2)

        cursor.execute(
            """INSERT INTO products (name, category, subcategory, price, cost, supplier_id, stock_quantity, weight, dimensions)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING product_id""",
            (
                subcategory, category, subcategory, price, cost,
                random.choice(suppliers), random.randint(0, 1000),
                round(random.uniform(0.5, 5.0), 2),
                "{}x{}x{}".format(random.randint(1, 50), random.randint(1, 50), random.randint(1, 50))
            )
        )
    
    conn.commit()

def insert_order_items(n=50):
    cursor.execute("SELECT order_id FROM orders")
    orders = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT product_id, price FROM products")
    products = cursor.fetchall()
    
    for i in range(1, n+1):
        order_id = random.choice(orders)
        product_id, price = random.choice(products) 
        quantity = random.randint(1, 5)
        discount = round(Decimal(random.uniform(0, 0.2)) * price * quantity, 2)
        total_price = round((price * quantity) - discount, 2)
        
        cursor.execute(
            """INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_amount, total_price)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (order_id, product_id, quantity, price, discount, total_price)
        )
    conn.commit()

def insert_product_reviews(n=150):
    cursor.execute("SELECT customer_id FROM customers")
    customers = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT product_id FROM products")
    products = [row[0] for row in cursor.fetchall()]
    
    for _ in range(n):
        cursor.execute(
            """INSERT INTO product_reviews (product_id, customer_id, rating, review_text, review_date)
               VALUES (%s, %s, %s, %s, %s)""",
            (
                random.choice(products), random.choice(customers), random.randint(1, 5),
                fake.text(max_nb_chars=200), fake.date_time_this_decade()
            )
        )
    conn.commit()


insert_customers()
insert_orders()
insert_suppliers()
insert_products()
insert_order_items()
insert_product_reviews()


cursor.close()
conn.close()
