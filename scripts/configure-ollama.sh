#!/usr/bin/env bash
set -euo pipefail

if [[ "${OLLAMA_SKIP_INSTALL:-}" == "1" ]]; then
  echo "Skipping Ollama configuration (OLLAMA_SKIP_INSTALL=1)"
  exit 0
fi

if ! command -v systemctl >/dev/null 2>&1; then
  echo "Skipping Ollama configuration (systemd not available)"
  exit 0
fi

DROP_IN_DIR="/etc/systemd/system/ollama.service.d"
DROP_IN_FILE="${DROP_IN_DIR}/jarvis.conf"

if [[ -f "$DROP_IN_FILE" ]]; then
  echo "Ollama Pi tuning already configured."
  exit 0
fi

echo "Applying Pi 4 memory tuning for Ollama..."
sudo mkdir -p "$DROP_IN_DIR"
sudo tee "$DROP_IN_FILE" >/dev/null <<'EOF'
[Service]
Environment="OLLAMA_MAX_LOADED_MODELS=1"
Environment="OLLAMA_KEEP_ALIVE=2m"
EOF

sudo systemctl daemon-reload
sudo systemctl restart ollama
echo "Ollama memory tuning applied."

# Optional: enable 2 GB swap on Raspberry Pi OS
# sudo dphys-swapfile swapoff
# sudo sed -i 's/CONF_SWAPSIZE=.*/CONF_SWAPSIZE=2048/' /etc/dphys-swapfile
# sudo dphys-swapfile setup && sudo dphys-swapfile swapon
