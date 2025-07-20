from flask import Flask, render_template, jsonify, request
import subprocess
import json
import os

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
    return render_template('index.html', state=last_values)

@app.route('/get-state', methods=['GET'])
def get_state():
    global last_values
    return jsonify(last_values)

@app.route('/control-device', methods=['POST'])
def control_device():
    global last_values
    data = request.get_json()
    topic = data.get('topic')
    value = data.get('value')

    if not topic or value is None:
        return jsonify(success=False, error="Missing 'topic' or 'value'"), 400

    success = publish_message(value, topic)
    if success:
        last_values[topic] = value
        save_state(last_values)
        return jsonify(success=True)
    else:
        return jsonify(success=False), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
