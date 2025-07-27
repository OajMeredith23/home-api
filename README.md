
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
- Create a `secrets.json` file and add your [openweathermap API key](https://home.openweathermap.org) to a variable called `WEATHER_API_KEY`


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
