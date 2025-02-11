import logging
import random


def validate_customer(customer):
    required_fields = ["customer_id", "first_name", "last_name", "age", "email", "country", "city", "postal_code", "phone_number", "registration_date", "last_login_date"]
    
    for field in required_fields:
        if field not in customer or not customer[field]:
            logging.warning(f"Invalid customer data: {customer}")
            return False
    return True

def generate_email(first_name, last_name):
    return f"{first_name.lower()}.{last_name.lower()}@example.com"

def generate_phone_number():
    return f"+{random.randint(100, 999)} {random.randint(10, 99)} {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}"