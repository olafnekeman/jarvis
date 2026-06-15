from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_CONFIG_PATH = PROJECT_ROOT / "config" / "models.toml"


@dataclass(frozen=True)
class AppConfig:
    ollama_host: str
    model_profile: str
    primary_model: str
    models: list[str]


def _detect_ram_profile() -> str:
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    kb = int(line.split()[1])
                    gb = kb / (1024 * 1024)
                    return "pi4_4gb" if gb < 6 else "pi4_8gb"
    except OSError:
        pass
    return "pi4_4gb"


def _load_models_config() -> dict:
    with MODELS_CONFIG_PATH.open("rb") as f:
        return tomllib.load(f)


def _resolve_profile(raw_config: dict, profile_override: str | None) -> str:
    if profile_override and profile_override != "auto":
        return profile_override

    default_profile = raw_config.get("default", {}).get("profile", "auto")
    if default_profile != "auto":
        return default_profile

    return _detect_ram_profile()


def load_config() -> AppConfig:
    raw = _load_models_config()
    profile = _resolve_profile(raw, os.environ.get("JARVIS_MODEL_PROFILE"))

    profiles = raw.get("profiles", {})
    if profile not in profiles:
        available = ", ".join(sorted(profiles))
        raise ValueError(
            f"Unknown model profile '{profile}'. Available profiles: {available}"
        )

    profile_config = profiles[profile]
    models = list(profile_config.get("models", []))
    if not models:
        raise ValueError(f"Profile '{profile}' has no models configured.")

    primary_model = os.environ.get("JARVIS_PRIMARY_MODEL", models[0])
    ollama_host = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")

    return AppConfig(
        ollama_host=ollama_host,
        model_profile=profile,
        primary_model=primary_model,
        models=models,
    )
