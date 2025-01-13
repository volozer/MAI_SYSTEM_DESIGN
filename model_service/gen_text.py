import tensorflow as tf
from tensorflow import keras
import numpy as np
import pandas as pd

from dotenv import load_dotenv

load_dotenv()

# Загрузка предобученной модели
loaded_model = keras.models.load_model("saved/my_model_with_vectorization.keras")

tickets_path = "data/all_tickets_processed_improved_v3.csv"
tickets_df = pd.read_csv(tickets_path)
# Уникальные категории
categories = sorted(tickets_df['Topic_group'].unique())
class_mapping = {i: category for i, category in enumerate(categories)}



def gen_category(input_text):
    # Преобразуем текст в тензор
    text_tensor = tf.constant([input_text], dtype=tf.string)

    # Предсказываем категорию
    predictions = loaded_model.predict(text_tensor)
    class_id = tf.argmax(predictions[0]).numpy()
    predicted_category = class_mapping.get(class_id, 'Unknown')
    return predicted_category