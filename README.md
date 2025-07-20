
# 🔌 Device Control API – Documentation

This API enables you to send MQTT messages to control devices via a unified endpoint. The backend uses a local Mosquitto broker to publish messages and stores device state persistently in a JSON file (`state.json`).

It is designed to interface with any MQTT subscriber, device code is [here](https://github.com/OajMeredith23/smart-home-devices)
---

## Getting started 

There's very little to configure here. 

- Ensure you have python3 installed correctly
- Create a `state.json` file at the root of this project containing an empty object. This wil be populated by MQTT requests and there messages. 

## 📍 Endpoint

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
