import json
import logging
import psycopg2
from datetime import datetime
from confluent_kafka import Consumer, KafkaException

from utilities import validate_customer
import settings


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

consumer_config = {
    'bootstrap.servers': settings.KAFKA_BROKER,
    'group.id': 'customer-group',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(consumer_config)
consumer.subscribe([settings.KAFKA_TOPIC])

conn = psycopg2.connect(
    dbname=settings.DB_NAME,
    user=settings.DB_USER,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
    port=settings.DB_PORT
)
cursor = conn.cursor()


def transform_customer(data):
    try:
        data["customer_id"] = int(data["customer_id"]) if str(data["customer_id"]).isdigit() else None
        if data["customer_id"] is None:
            logging.warning(f"Skipping record due to invalid customer_id ({data['age']}): {data}")
        data["first_name"] = data["first_name"].strip().title()
        data["last_name"] = data["last_name"].strip().title()
        data["age"] = int(data["age"]) if str(data["age"]).isdigit() else None
        if data["age"] is None or data["age"] <= 0:
            logging.warning(f"Skipping record due to invalid age ({data['age']}): {data}")
        data["email"] = data["email"].strip().lower()
        data["phone_number"] = data["phone_number"].replace(" ", "")
        data["registration_date"] = datetime.strptime(data["registration_date"], "%Y-%m-%d %H:%M:%S")
        data["last_login_date"] = datetime.strptime(data["last_login_date"], "%Y-%m-%d %H:%M:%S")
    except Exception as e:
        logging.error(f"Error transforming customer data: {data} - {e}")
        return None
    return data

def consume_messages():
    while True:
        try:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())

            customer = json.loads(msg.value().decode("utf-8"))

            if validate_customer(customer):
                transformed_data = transform_customer(customer)

                if transformed_data:
                    cursor.execute(
                        """INSERT INTO customers (customer_id, first_name, last_name, age, email, country, city, postal_code, phone_number, registration_date, last_login_date)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (
                            transformed_data["customer_id"], transformed_data["first_name"], transformed_data["last_name"],
                            transformed_data["age"], transformed_data["email"], transformed_data["country"], transformed_data["city"], 
                            transformed_data["postal_code"], transformed_data["phone_number"], transformed_data["registration_date"],
                            transformed_data["last_login_date"]
                        )
                    )
                    conn.commit()
                    logging.info(f"Inserted into DB: {transformed_data}")
                else:
                    logging.warning(f"Skipping transformation failed data: {customer}")
            else:
                logging.warning(f"Skipping invalid data: {customer}")

        except Exception as e:
            logging.error(f"Kafka Consumer Error: {e}")

if __name__ == "__main__":
    logging.info(f"Kafka Consumer is running, listening to topic '{settings.KAFKA_TOPIC}'...")
    consume_messages()
