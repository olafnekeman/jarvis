from __future__ import annotations

import sys
import time
from typing import Any

import ollama
from ollama import Client, ResponseError

DEFAULT_HOST = "http://127.0.0.1:11434"
SERVER_WAIT_TIMEOUT = 60
SERVER_POLL_INTERVAL = 2


class OllamaNotReadyError(RuntimeError):
    pass


class ModelNotFoundError(RuntimeError):
    pass


def _client(host: str = DEFAULT_HOST) -> Client:
    return Client(host=host)


def _installed_model_names(client: Client) -> set[str]:
    response = client.list()
    return {model.model for model in response.models}


def _is_model_installed(requested: str, installed: set[str]) -> bool:
    if requested in installed:
        return True
    return any(name.startswith(f"{requested}:") for name in installed)


def wait_for_server(
    host: str = DEFAULT_HOST,
    timeout: int = SERVER_WAIT_TIMEOUT,
) -> None:
    client = _client(host)
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None

    while time.monotonic() < deadline:
        try:
            client.list()
            return
        except Exception as exc:
            last_error = exc
            time.sleep(SERVER_POLL_INTERVAL)

    message = (
        f"Ollama server at {host} did not become ready within {timeout}s. "
        "Run ./scripts/setup.sh to install and start Ollama."
    )
    if last_error is not None:
        message = f"{message} Last error: {last_error}"
    raise OllamaNotReadyError(message)


def _print_pull_progress(name: str, progress: Any) -> None:
    status = getattr(progress, "status", None) or ""
    completed = getattr(progress, "completed", None)
    total = getattr(progress, "total", None)

    if completed is not None and total:
        pct = round(completed / total * 100, 1)
        line = f"[{name}] {status} — {pct}%"
    else:
        line = f"[{name}] {status}"

    print(line, file=sys.stderr, end="\r", flush=True)

    if status == "success":
        print(file=sys.stderr)


def ensure_models(models: list[str], host: str = DEFAULT_HOST) -> None:
    wait_for_server(host=host)
    client = _client(host)
    installed = _installed_model_names(client)

    for name in models:
        if _is_model_installed(name, installed):
            print(f"Model already installed: {name}")
            continue

        print(f"Pulling model: {name}")
        try:
            for progress in client.pull(name, stream=True):
                _print_pull_progress(name, progress)
        except ResponseError as exc:
            raise RuntimeError(
                f"Failed to pull model '{name}': {exc.error}. "
                "Try a smaller model profile with JARVIS_MODEL_PROFILE=pi4_4gb."
            ) from exc

        installed = _installed_model_names(client)


def check_models(models: list[str], host: str = DEFAULT_HOST) -> list[str]:
    client = _client(host)
    installed = _installed_model_names(client)
    return [name for name in models if not _is_model_installed(name, installed)]


def chat(
    model: str,
    messages: list[dict[str, str]],
    host: str = DEFAULT_HOST,
    **kwargs: Any,
) -> dict[str, Any]:
    client = _client(host)
    try:
        return client.chat(model=model, messages=messages, **kwargs)
    except ResponseError as exc:
        if exc.status_code == 404:
            raise ModelNotFoundError(
                f"Model '{model}' is not installed. Run 'jarvis setup' to download it."
            ) from exc
        raise
