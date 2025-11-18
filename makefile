DEV_VENV=venv-dev
PROD_VENV_API=venv-api
PROD_VENV_MQTT=venv-mqtt

.PHONY: setup dev prod stop-dev diagnostics

# ----------------------------------------
# Setup: create dev environment + files
# ----------------------------------------
setup:
	@echo "🔧 Creating development virtual environment..."
	python3 -m venv $(DEV_VENV)

	@echo "📦 Installing dependencies..."
	source $(DEV_VENV)/bin/activate && pip install -r requirements.txt && pip install watchfiles

	@echo "📁 Ensuring required files exist..."

	@test -f state.json || echo "{}" > state.json

	# Create env.py only if missing (won't overwrite your real key)
	@test -f env.py || echo 'WEATHER_API_KEY = ""' > env.py

	@echo "✅ Setup complete!"
	@echo "👉 Add your real API key to env.py"


# ----------------------------------------
# Development mode: stop systemd + run both dev servers
# ----------------------------------------
dev:
	@echo "⏹️ Stopping systemd services (production mode)..."
	sudo systemctl stop device-api || true
	sudo systemctl stop mqtt-listener || true

	@echo "🚀 Starting development mode:"
	@echo "   - Flask API (app.py, auto reload)"
	@echo "   - MQTT Listener (run_mqtt_dev.py, auto restart)"

	# Use venv python directly (no 'source' needed)
	$(DEV_VENV)/bin/python app.py &
	$(DEV_VENV)/bin/python run_mqtt_dev.py &
	wait


# ----------------------------------------
# Back to production services (systemd)
# ----------------------------------------
prod:
	@echo "▶️ Starting production systemd services..."
	sudo systemctl start device-api
	sudo systemctl start mqtt-listener
	@echo "✅ Production services running."


# ----------------------------------------
# Stop all dev processes
# ----------------------------------------
stop-dev:
	@echo "⏹️ Stopping development processes..."
	pkill -f "python app.py" || true
	pkill -f "run_mqtt_dev.py" || true


# ----------------------------------------
# Diagnostics: show what's running
# ----------------------------------------
diagnostics:
	@echo "🔍 Diagnostics:"
	@echo
	@echo "🟦 Systemd service status:"
	@echo "---------------------------------------------------"
	-systemctl is-active device-api
	-systemctl is-active mqtt-listener
	@echo
	@echo "🟩 Systemd logs (last few lines):"
	@echo "---------------------------------------------------"
	@echo "device-api:"; sudo journalctl -u device-api -n 3 --no-pager
	@echo "mqtt-listener:"; sudo journalctl -u mqtt-listener -n 3 --no-pager
	@echo
	@echo "🟧 Development processes running?"
	@echo "---------------------------------------------------"
	-ps aux | grep -E "app.py|run_mqtt_dev.py" | grep python || echo "No dev processes running."
	@echo
	@echo "🌐 Network listeners on port 5000 (API):"
	@echo "---------------------------------------------------"
	-sudo lsof -i :5000 || echo "Nothing running on port 5000"
	@echo
	@echo "🪁 MQTT listeners (connecting to mosquitto):"
	@echo "---------------------------------------------------"
	-pgrep -af mqtt_status_listener.py || echo "No MQTT dev listener running."
	@echo
	@echo "✨ Diagnostics complete."

.PHONY: logs

logs:
	@echo "📜 Checking log source..."
	@if systemctl is-active --quiet device-api; then \
		echo "🟦 Production API is running via systemd. Streaming logs..."; \
		sudo journalctl -u device-api -f; \
	else \
		echo "🟧 Device API is NOT running under systemd."; \
		echo "   If you're in development mode, logs already appear in your terminal."; \
		echo "   (Started via 'make dev')"; \
	fi
