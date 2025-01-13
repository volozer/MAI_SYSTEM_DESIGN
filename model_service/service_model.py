import os
import logging
from kafka import KafkaProducer, KafkaConsumer
from dotenv import load_dotenv

import gen_text # Импорт функции предсказания из другого файла

load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def start_kafka_server():
    producer = KafkaProducer(
        bootstrap_servers=os.getenv('KAFKA_BROKER', 'localhost:9092'),
        value_serializer=lambda v: v.encode('utf-8')
    )
    consumer = KafkaConsumer(
        'input_texts',  
        bootstrap_servers=os.getenv('KAFKA_BROKER', 'localhost:9092'),
        value_deserializer=lambda v: v.decode('utf-8') 
    )
    logger.info("Kafka server started")


    for msg in consumer:
        logger.info(f"Received message: {msg.value}")

        input_text = msg.value 
        try:
            predicted_category = gen_text(input_text)
            logger.info(f"Predicted category: {predicted_category}")

            producer.send('predicted_categories', value=predicted_category)
            producer.flush() 
            logger.info(f"Sent category '{predicted_category}' to 'predicted_categories'")
        except Exception as e:
            logger.error(f"Error processing message '{msg.value}': {e}")

if __name__ == "__main__":
    start_kafka_server()
