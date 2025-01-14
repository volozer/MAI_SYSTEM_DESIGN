import os
import logging
import asyncio
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from dotenv import load_dotenv

import gen_text

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def start_kafka_server():
    producer = AIOKafkaProducer(bootstrap_servers='broker:29090')
    consumer = AIOKafkaConsumer(
        'server',
        bootstrap_servers='broker:29090',
        group_id='server-group',
        enable_auto_commit=True,
        auto_offset_reset='earliest'
    )

    await producer.start()
    await consumer.start()
    logger.info("Kafka server started")

    try:
        async for msg in consumer:
            logger.info(f"Received message: {msg.value.decode('utf-8')}")
            input_text = msg.value.decode('utf-8')
            try:
                predicted_category = gen_text(input_text)
                logger.info(f"Predicted category: {predicted_category}")

                await producer.send_and_wait('predicted_categories', value=predicted_category.encode('utf-8'))
                logger.info(f"Sent category '{predicted_category}' to 'predicted_categories'")
            except Exception as e:
                logger.error(f"Error processing message '{msg.value.decode('utf-8')}': {e}")
    finally:
        await producer.stop()
        await consumer.stop()

if __name__ == "__main__":
    asyncio.run(start_kafka_server())
