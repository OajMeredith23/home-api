import subprocess
import json
import time
import threading

STATE_FILE = 'state.json'
TIMEOUT = 45  # seconds

last_ping_time = 0
lock = threading.Lock()

def save_status(status):
    try:
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        state = {}

    state['pico/status'] = status

    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def monitor_timeout():
    global last_ping_time
    while True:
        time.sleep(5)
        with lock:
            elapsed = time.time() - last_ping_time
            if elapsed > TIMEOUT:
                print("No heartbeat received in 45 seconds, setting status to 'offline'")
                save_status('offline')

def listen():
    global last_ping_time

    # Start the timeout monitor thread
    threading.Thread(target=monitor_timeout, daemon=True).start()

    p = subprocess.Popen(
        ['mosquitto_sub', '-h', 'localhost', '-t', 'pico/status'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    for line in p.stdout:
        payload = line.strip()
        print(f"Received pico/status: {payload}")
        with lock:
            last_ping_time = time.time()
        save_status(payload)

if __name__ == '__main__':
    last_ping_time = time.time()  # initialize at start
    listen()
