import logging

def validate_customer(customer):
    required_fields = ["customer_id", "first_name", "last_name", "age", "email", "country", "city", "postal_code", "phone_number", "registration_date", "last_login_date"]
    
    for field in required_fields:
        if field not in customer or not customer[field]:
            logging.warning(f"Invalid customer data: {customer}")
            return False
    return True