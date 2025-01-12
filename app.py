from flask import Flask, request, jsonify, render_template
import tensorflow as tf
from tensorflow import keras
import numpy as np
import pandas as pd

# Загрузка предобученной модели
loaded_model = keras.models.load_model("saved/my_model_with_vectorization.keras")

tickets_path = "data/all_tickets_processed_improved_v3.csv"
tickets_df = pd.read_csv(tickets_path)
# Уникальные категории
categories = sorted(tickets_df['Topic_group'].unique())
class_mapping = {i: category for i, category in enumerate(categories)}


app = Flask(__name__)

# Главная страница (HTML форма для ввода текста)
@app.route('/')
def index():
    return render_template('index.html')  

# Маршрут для предсказания
@app.route('/predict', methods=['POST'])
def predict():
    # Получаем текст из формы
    input_text = request.form['text']
    
    # Преобразуем текст в тензор
    text_tensor = tf.constant([input_text], dtype=tf.string)

    # Предсказываем категорию
    predictions = loaded_model.predict(text_tensor)
    class_id = tf.argmax(predictions[0]).numpy()
    predicted_category = class_mapping[class_id]
    
    # Возвращаем результат в формате JSON
    return jsonify({'input_text': input_text, 'predicted_category': predicted_category})

if __name__ == '__main__':
    app.run(debug=True)
