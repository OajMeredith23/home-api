from flask import Flask, render_template, jsonify, request
import requests
import subprocess
import json
import os
from secrets import WEATHER_API_KEY

app = Flask(__name__)

MQTT_HOST = 'localhost'
STATE_FILE = 'state.json'

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

last_values = load_state()

def publish_message(message, topic):
    cmd = ['mosquitto_pub', '-h', MQTT_HOST, '-t', topic, '-m', str(message)]
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"MQTT publish failed: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html', state=load_state())

@app.route('/get-state', methods=['GET'])
def get_state():
    return jsonify(load_state())

@app.route('/control-device', methods=['POST'])
def control_device():
    global last_values
    data = request.get_json()
    topic = data.get('topic')
    value = data.get('value')

   

    if not topic or value is None:
        return jsonify(success=False, error="Missing 'topic' or 'value'"), 400

    # Derive the device name from the first segment of the topic
    device = topic.split('/')[0] if topic else None
    if load_state()[f"{device}/status"] == 'offline':
        return jsonify(success=False, error=f"Device {device} is offline."), 503

    success = publish_message(value, topic)
    if success:
        last_values[topic] = value
        save_state(last_values)
        return jsonify(success=True)
    else:
        return jsonify(success=False), 500


@app.route('/weather', methods=['GET'])
def weather():
    weather_url = f'https://api.openweathermap.org/data/2.5/weather?lat=51.39532529262788&lon=0.008861501686488386&&appid={WEATHER_API_KEY}&units=metric'
    weather = requests.get(weather_url).json()

    return jsonify(weather)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
