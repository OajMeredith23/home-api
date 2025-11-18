
# 🔌 Home API – Documentation

This API has multiple utilities. 

- It allows you to send MQTT messages to control devices via a unified endpoint. The backend uses a local Mosquitto broker to publish messages and stores device state persistently in a JSON file (`state.json`). It is designed to interface with any MQTT subscriber, custom device code is [here](https://github.com/OajMeredith23/smart-home-devices)
- It has endpoints that return datasets. Like the `/weather` endpoint that returns weather data for Bromley.

For more details and example on available endpoints import the `postman-collection.yml` file into Postman.
---

## Getting started 

There's very little to configure here. 

- Ensure you have python3 installed correctly
- Create a `state.json` file at the root of this project containing an empty object. This wil be populated by MQTT requests and their messages. 
- Create a `env.py` file and add your [openweathermap API key](https://home.openweathermap.org) to a variable called `WEATHER_API_KEY`


# Getting Started: Running the API and MQTT Listener as systemd Services

This guide will help you get both the Flask API and the MQTT listener running as separate systemd services on your Raspberry Pi or Linux machine.

---

## Prerequisites

- Python 3 installed
- `mosquitto` MQTT broker installed and running
- Git to clone the repository

---

## Step 1: Clone the repository

```bash
git clone https://github.com/yourusername/yourrepo.git
cd yourrepo
```

### Step 2: Create virtual environments and install dependencies



```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
```

Alternatively, you can use the provided `Makefile` which automates setup and common development tasks (recommended).

## Using the Makefile (recommended)

This repository includes a `Makefile` with targets to create virtual environments, install dependencies, run the API and MQTT listener in development mode, and manage production systemd services. It uses these default venv names:

- `venv-dev` — development virtual environment used by `make setup` and `make dev`
- `venv-api` — production virtual environment for the API (used by systemd/service files)
- `venv-mqtt` — production virtual environment for the MQTT listener (used by systemd/service files)

Common targets:

- `make setup` — create `venv-dev`, install dependencies from `requirements.txt`, install `watchfiles`, and ensure `state.json` and a placeholder `env.py` exist.
- `make dev` — stop the `device-api` and `mqtt-listener` systemd services (if running) and start the Flask API and MQTT listener in development mode using `venv-dev` (auto-reload / auto-restart behavior).
- `make prod` — start the production systemd services (`device-api` and `mqtt-listener`).
- `make stop-dev` — stop development processes started by `make dev`.
- `make diagnostics` — run quick status checks for systemd services, dev processes, and listeners.
- `make logs` — stream production API logs if the `device-api` service is running under systemd.

Quick examples:

```bash
# Run initial project setup (creates venv-dev and placeholder env.py)
make setup

# Start the API and MQTT listener in development mode (uses venv-dev)
make dev

# Stop development processes
make stop-dev

# Show quick diagnostics
make diagnostics

# Stream production API logs (if running under systemd)
make logs
```

Notes:

- After `make setup` add your OpenWeatherMap API key to `env.py` as:

```python
WEATHER_API_KEY = "your_api_key_here"
```

- `state.json` will be created by `make setup` if missing and stores device state persisted by the API.
- `make dev` stops systemd services so the dev-run processes can bind to the standard ports (like :5000).

### Local development with `make dev`

`make dev` is the recommended way to run the API and MQTT listener locally while developing. It does the following:

- Stops the production systemd services `device-api` and `mqtt-listener` (if they are running) so the dev processes can bind to port 5000 and any MQTT ports without conflict.
- Starts the Flask API (`app.py`) and the development MQTT listener (`run_mqtt_dev.py`) using the `venv-dev` virtual environment.
- Runs both processes in the foreground so you see logs in your terminal. The Makefile launches them and waits; use the same terminal session to observe output.

How to run:

```bash
# Ensure you have run setup once (creates venv-dev and installs deps)
make setup

# Start the dev servers (press Ctrl+C to stop or use `make stop-dev` from another shell)
make dev
```

Stopping and troubleshooting:

- To stop dev mode from another terminal use:

```bash
make stop-dev
```

- If the dev processes don't start, check `state.json` exists and `env.py` contains `WEATHER_API_KEY` (or an empty placeholder is fine for local testing).
- If ports are in use, run `make stop-dev` and verify systemd services are stopped or use `sudo lsof -i :5000` to find conflicting processes.

Tip: Run `make diagnostics` to get quick status information about systemd services and development processes.

### Step 3: Create systemd service files

#### 3a. Flask API service
Create `/etc/systemd/system/device-api.service` with the following content:

```ini
[Unit]
Description=Device Control Flask API
After=network.target

[Service]
User=your-username
WorkingDirectory=/full/path/to/yourrepo
ExecStart=/full/path/to/yourrepo/venv-api/bin/python3 /full/path/to/yourrepo/app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
3b. MQTT Listener service
Create /etc/systemd/system/mqtt-listener.service with the following content:
```

```ini
[Unit]
Description=MQTT Status Listener
After=network.target

[Service]
User=your-username
WorkingDirectory=/full/path/to/yourrepo
ExecStart=/full/path/to/yourrepo/venv-mqtt/bin/python3 /full/path/to/yourrepo/mqtt_status_listener.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
Replace your-username and /full/path/to/yourrepo with your actual Linux username and the absolute path to the cloned repo.
Step 4: Enable and start the services
```
Reload systemd to apply changes:

```bash
sudo systemctl daemon-reload
```
Enable the services to start on boot:

```bash
sudo systemctl enable device-api.service
sudo systemctl enable mqtt-listener.service
```

Start the services now:

```bash
sudo systemctl start device-api.service
sudo systemctl start mqtt-listener.service
```

Step 5: Verify the services are running

Check their status:

```bash
sudo systemctl status device-api.service
sudo systemctl status mqtt-listener.service
```

Use logs to debug if needed:

```bash
sudo journalctl -u device-api.service -f
sudo journalctl -u mqtt-listener.service -f
```

Summary

Two separate virtual environments ensure isolated dependencies
Two systemd services auto-start on boot and auto-restart on failure
Logs are accessible via journalctl
If you want to modify the services (e.g., change ports or MQTT topics), edit the Python scripts and reload systemd with:

```bash
sudo systemctl daemon-reload
sudo systemctl restart device-api.service
sudo systemctl restart mqtt-listener.service
```

# Using MQTT 

## 📍 Control device endpoint

```
POST /control-device
```

---

## 📦 Request Format

### Headers
```http
Content-Type: application/json
```

### JSON Body

```json
{
  "topic": "pico/led/brightness",
  "value": 75
}
```

| Field   | Type   | Required | Description                                     |
|---------|--------|----------|-------------------------------------------------|
| `topic` | string | ✅ Yes   | MQTT topic to publish to (e.g. `pico/led`)     |
| `value` | any    | ✅ Yes   | The value/message to publish (e.g. `on`, `75`) |

---

## ✅ Successful Response

```json
{
  "success": true
}
```

### Status Code: `200 OK`

---

## ❌ Error Responses

### Missing Fields

```json
{
  "success": false,
  "error": "Missing 'topic' or 'value'"
}
```

**Status Code:** `400 Bad Request`

---

### MQTT Failure

```json
{
  "success": false
}
```

**Status Code:** `500 Internal Server Error`

---

## 🧠 Notes

- **All device states are saved** in `state.json` for persistence.
- New topics are **automatically added** — no need to predefine them.
- Messages are published via `mosquitto_pub` to a local MQTT broker.

---

## 🧪 Example `curl` Request

```bash
curl -X POST http://<your-raspberrypi-ip>:5000/control-device \
  -H "Content-Type: application/json" \
  -d '{"topic": "pico/led", "value": "on"}'
```

Or for setting brightness:

```bash
curl -X POST http://<your-raspberrypi-ip>:5000/control-device \
  -H "Content-Type: application/json" \
  -d '{"topic": "pico/led/brightness", "value": 90}'
```
