from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import json
import os

app = Flask(__name__)

# Инициализация Flask-Limiter с использованием in-memory backend
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per day"]  # Общее ограничение: 100 запросов в день
)

# Глобальная переменная для хранения данных
DATA_FILE = "data.json"
data = {}

# Функция для загрузки данных из файла
def load_data():
    global data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            data = json.load(file)
    else:
        data = {}

# Функция для сохранения данных в файл
def save_data():
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Загрузка данных при старте приложения
load_data()

# Маршрут для сохранения ключ-значения
@app.route("/set", methods=["POST"])
@limiter.limit("10 per minute")  # Ограничение: 10 запросов в минуту
def set_value():
    global data
    req_data = request.get_json()
    key = req_data.get("key")
    value = req_data.get("value")

    if not key or value is None:
        return jsonify({"error": "Key and value are required."}), 400

    data[key] = value
    save_data()
    return jsonify({"message": "Key-value pair saved successfully."}), 200

# Маршрут для получения значения по ключу
@app.route("/get/<key>", methods=["GET"])
def get_value(key):
    value = data.get(key)
    if value is None:
        return jsonify({"error": "Key not found."}), 404
    return jsonify({"key": key, "value": value}), 200

# Маршрут для удаления ключа
@app.route("/delete/<key>", methods=["DELETE"])
@limiter.limit("10 per minute")  # Ограничение: 10 запросов в минуту
def delete_key(key):
    if key in data:
        del data[key]
        save_data()
        return jsonify({"message": "Key deleted successfully."}), 200
    return jsonify({"error": "Key not found."}), 404

# Маршрут для проверки наличия ключа
@app.route("/exists/<key>", methods=["GET"])
def key_exists(key):
    exists = key in data
    return jsonify({"key": key, "exists": exists}), 200

if __name__ == "__main__":
    app.run(debug=True)
    

