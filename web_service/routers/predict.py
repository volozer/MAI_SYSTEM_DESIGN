from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import asyncio
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Константы
KAFKA_BROKER = "kafka:29092"
INPUT_TOPIC = "input_topic"
OUTPUT_TOPIC = "output_topic"
GROUP_ID = "my-group"

# Инициализация маршрутизатора
router = APIRouter(
    prefix="/predict",
    tags=["category"]
)

# Инициализация Kafka Producer и Consumer
producer = None
consumer = None

async def initialize_kafka():
    global producer, consumer
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BROKER)
    consumer = AIOKafkaConsumer(
        OUTPUT_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        group_id=GROUP_ID,
        enable_auto_commit=True,
        auto_offset_reset="earliest",
    )
    await producer.start()
    await consumer.start()

@router.on_event("startup")
async def startup_event():
    await initialize_kafka()

@router.on_event("shutdown")
async def shutdown_event():
    global producer, consumer
    if producer:
        await producer.stop()
    if consumer:
        await consumer.stop()

@router.post('/')
async def predict(request: Request):
    # Получаем текст из формы
    form_data = await request.form()
    input_text = form_data.get('text')

    if not input_text:
        return JSONResponse({'error': 'No input text provided'}, status_code=400)

    # Отправляем input_text в Kafka
    try:
        await producer.send_and_wait(INPUT_TOPIC, input_text.encode('utf-8'))
        print(f"Sent input_text to Kafka: {input_text}")
    except Exception as e:
        return JSONResponse({'error': f"Failed to send message to Kafka: {e}"}, status_code=500)

    # Асинхронное ожидание ответа из Kafka
    try:
        predicted_category = await get_prediction_from_kafka(input_text)
    except asyncio.TimeoutError:
        return JSONResponse({'error': 'Prediction timeout exceeded'}, status_code=504)

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
    global consumer
    try:
        async for message in consumer:
            predicted_category = message.value.decode('utf-8')
            print(f"Received from Kafka: {predicted_category}")

            # Если нашли нужный результат, возвращаем
            if input_text in predicted_category:
                return predicted_category
    
    except Exception as e:
        print(f"Error while consuming messages: {e}")

    # Если тайм-аут или другая ошибка
    raise asyncio.TimeoutError("Timeout while waiting for prediction")
