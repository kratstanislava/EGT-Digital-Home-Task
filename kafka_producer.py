import json
import random
import time
import logging
from faker import Faker
from confluent_kafka import Producer

from utilities import generate_email, generate_phone_number, validate_customer
import settings


fake = Faker(['en_GB'])

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

producer_config = {
    'bootstrap.servers': settings.KAFKA_BROKER,
    'client.id': 'customer-producer'
}

producer = Producer(producer_config)


def delivery_report(err, msg):
    if err is not None:
        logging.error(f"Message delivery failed: {err}")
    else:
        logging.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def validate_customer(customer):
    required_fields = ["customer_id", "first_name", "last_name", "age", "email", "country", "city", "postal_code", "phone_number", "registration_date", "last_login_date"]
    
    for field in required_fields:
        if field not in customer or not customer[field]:
            logging.warning(f"Invalid customer data: {customer}")
            return False
    return True

def generate_customer():
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = generate_email(first_name, last_name)
    phone_number = generate_phone_number()
    
    return {
        "customer_id": random.randint(1000, 9999),
        "first_name": first_name,
        "last_name": last_name,
        "age": random.randint(18, 70),
        "email": email,
        "country": fake.country(),
        "city": fake.city(),
        "postal_code": fake.postcode(),
        "phone_number": phone_number,
        "registration_date": str(fake.date_time_between(start_date="-5y", end_date="-1y")),
        "last_login_date": str(fake.date_time_this_year())
    }

def send_to_kafka():
    while True:
        customer = generate_customer()
        
        if validate_customer(customer):
            customer_json = json.dumps(customer)

            try:
                producer.produce(
                    settings.KAFKA_TOPIC, 
                    key=str(customer["customer_id"]), 
                    value=customer_json, 
                    callback=delivery_report
                )
                producer.poll(0)
                logging.info(f"Sent: {customer_json}")
            except Exception as e:
                logging.error(f"Kafka Producer Error: {e}")

        time.sleep(2)

if __name__ == "__main__":
    logging.info(f"Kafka Producer is running, sending messages to topic '{settings.KAFKA_TOPIC}'...")
    send_to_kafka()
