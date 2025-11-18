from watchfiles import watch
import subprocess
import sys
import os

def run():
    # Start the MQTT listener
    process = subprocess.Popen([sys.executable, "mqtt_status_listener.py"])
    print("MQTT listener started with PID", process.pid)
    return process

if __name__ == "__main__":
    process = run()

    # Watch the .py files for changes
    def _py_filter(change, path):
        return path.endswith('.py')

    for changes in watch('.', watch_filter=_py_filter):
        print("Changes detected:", changes)
        process.terminate()
        process.wait()
        print("Restarting MQTT listener...")
        process = run()
