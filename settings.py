import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME=os.getenv('DB_NAME', 'postgres')
DB_USER=os.getenv('DB_USER', 'username')
DB_PASSWORD=os.getenv('DB_PASSWORD', 'password')
DB_HOST=os.getenv('DB_HOST', '127.0.0.1')
DB_PORT=os.getenv('DB_PORT', '5432')

KAFKA_BROKER="localhost:9092"
KAFKA_TOPIC="customers"
