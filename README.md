# jarvis

Home automation with LLMs, designed to run on a Raspberry Pi 4 with Ollama.

## Requirements

- Raspberry Pi 4 (4 GB or 8 GB RAM)
- Raspberry Pi OS **64-bit** (Bookworm or later)
- At least 3 GB free disk space per model
- Active cooling recommended
- SSD strongly recommended (microSD works but model loads are slow)

## Quick start

Clone and run the setup script:

```bash
git clone https://github.com/olafnekeman/jarvis.git
cd jarvis
chmod +x scripts/setup.sh
./scripts/setup.sh
```

Or install with a single command:

```bash
curl -fsSL https://raw.githubusercontent.com/olafnekeman/jarvis/main/install.sh | bash
```

The setup script will:

1. Verify your Pi hardware (64-bit OS, RAM, disk space)
2. Install Ollama and start it as a system service
3. Apply Pi 4 memory tuning for Ollama
4. Install Python dependencies with [uv](https://docs.astral.sh/uv/)
5. Download the models defined in `config/models.toml`
6. Run a health check with `jarvis doctor`

## Model profiles

Models are declared in [`config/models.toml`](config/models.toml) and selected automatically based on available RAM:

| Profile   | RAM   | Models                          |
|-----------|-------|---------------------------------|
| `pi4_4gb` | ~4 GB | `qwen2.5:0.5b`                  |
| `pi4_8gb` | ~8 GB | `qwen2.5:1.5b`, `llama3.2:1b`  |

Override the profile:

```bash
export JARVIS_MODEL_PROFILE=pi4_4gb
./scripts/setup.sh
```

## CLI commands

```bash
uv run jarvis setup    # Download required models (safe to re-run)
uv run jarvis doctor   # Check Ollama server and installed models
uv run jarvis run      # Start jarvis
```

## Configuration

Copy [`.env.example`](.env.example) to `.env` to override defaults:

```
OLLAMA_HOST=http://127.0.0.1:11434
JARVIS_MODEL_PROFILE=pi4_4gb
JARVIS_PRIMARY_MODEL=qwen2.5:0.5b
```

## Local development (Mac/Linux)

Develop against a local Ollama instance without running the Pi installer:

```bash
export OLLAMA_SKIP_INSTALL=1
uv sync
uv run jarvis setup
uv run jarvis doctor
```

## Troubleshooting

**Ollama not running**

```bash
sudo systemctl status ollama
journalctl -u ollama --no-pager -n 30
```

**Out of memory**

Switch to the smaller model profile:

```bash
export JARVIS_MODEL_PROFILE=pi4_4gb
uv run jarvis setup
```

**Model not found at runtime**

```bash
uv run jarvis setup
```

## Project structure

```
jarvis/
├── config/models.toml       # Model manifest (RAM profiles)
├── scripts/
│   ├── setup.sh             # One-command setup entry point
│   ├── preflight.sh         # Hardware checks
│   ├── install-ollama.sh    # Idempotent Ollama install
│   └── configure-ollama.sh  # Pi 4 memory tuning
└── jarvis/
    ├── cli.py               # setup, doctor, run commands
    ├── config.py            # Load manifest + env overrides
    └── ollama.py            # Server checks, model pulls, chat wrapper
```
