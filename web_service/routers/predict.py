from fastapi import APIRouter, Request, Form
from fastapi.responses import JSONResponse
from kafka import KafkaProducer, KafkaConsumer
import os
import asyncio
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Инициализация маршрутизатора
router = APIRouter(
    prefix="/predict",
    tags=["category"]
)

# Конфигурация Kafka
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
INPUT_TOPIC = 'input_texts'
OUTPUT_TOPIC = 'predicted_categories'

# Инициализация Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: v.encode('utf-8')
)

# Инициализация Kafka Consumer
consumer = KafkaConsumer(
    OUTPUT_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda v: v.decode('utf-8'),
    group_id='fastapi_group',
    auto_offset_reset='earliest'  # Читаем сообщения с начала
)

@router.post('/')
async def predict(request: Request):
    # Получаем текст из формы
    form_data = await request.form()
    input_text = form_data.get('text')

    if not input_text:
        return JSONResponse({'error': 'No input text provided'}, status_code=400)

    # Отправляем input_text в Kafka
    producer.send(INPUT_TOPIC, value=input_text)
    producer.flush()
    
    # Логируем отправку
    print(f"Sent input_text to Kafka: {input_text}")

    # Асинхронное ожидание ответа из Kafka
    predicted_category = await get_prediction_from_kafka(input_text)

    # Возвращаем результат в формате JSON
    return JSONResponse({
        'input_text': input_text,
        'predicted_category': predicted_category
    })


async def get_prediction_from_kafka(input_text: str, timeout: int = 10):
    """
    Слушаем Kafka Consumer для получения предсказания.
    :param input_text: текст, отправленный в Kafka.
    :param timeout: максимальное время ожидания (в секундах).
    :return: предсказанная категория.
    """
    loop = asyncio.get_event_loop()
    future = loop.run_in_executor(None, fetch_prediction, input_text, timeout)
    return await future


def fetch_prediction(input_text: str, timeout: int):
    """
    Блокирующий вызов для получения предсказания из Kafka Consumer.
    :param input_text: текст, отправленный в Kafka.
    :param timeout: максимальное время ожидания (в секундах).
    :return: предсказанная категория.
    """
    import time
    start_time = time.time()
    
    for message in consumer:
        predicted_category = message.value
        print(f"Received from Kafka: {predicted_category}")

        # Если нашли нужный результат, возвращаем
        if input_text in predicted_category:
            return predicted_category

        # Если вышли за пределы таймаута, возвращаем ошибку
        if time.time() - start_time > timeout:
            return 'Prediction timeout exceeded'

    return 'Prediction not found'
