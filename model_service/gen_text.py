from tensorflow import keras
import numpy as np
import pandas as pd

from dotenv import load_dotenv
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1' 

import tensorflow as tf

load_dotenv()

try:
    loaded_model = keras.models.load_model("saved/my_model_with_vectorization.keras")
    print("Модель загружена успешно.")
except Exception as e:
    print(f"Ошибка загрузки модели: {e}")

tickets_path = "data/all_tickets_processed_improved_v3.csv"
tickets_df = pd.read_csv(tickets_path)
categories = sorted(tickets_df['Topic_group'].unique())
class_mapping = {i: category for i, category in enumerate(categories)}



def gen_category(input_text):
    text_tensor = tf.constant([input_text], dtype=tf.string)

    predictions = loaded_model.predict(text_tensor)
    class_id = tf.argmax(predictions[0]).numpy()
    predicted_category = class_mapping.get(class_id, 'Unknown')
    return predicted_category


def test():
    input_text = "some text"
    text = gen_category(input_text)
    print("some text: ", text)

# test()