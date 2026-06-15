from __future__ import annotations

import argparse
import sys

from dotenv import load_dotenv

from jarvis import __version__
from jarvis.config import load_config
from jarvis.ollama import (
    OllamaNotReadyError,
    check_models,
    ensure_models,
    wait_for_server,
)


def _cmd_setup(_args: argparse.Namespace) -> int:
    config = load_config()
    print(f"Using model profile: {config.model_profile}")
    print(f"Ollama host: {config.ollama_host}")
    print(f"Models: {', '.join(config.models)}")

    try:
        ensure_models(config.models, host=config.ollama_host)
    except OllamaNotReadyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print("Setup complete.")
    return 0


def _cmd_doctor(_args: argparse.Namespace) -> int:
    config = load_config()
    ok = True

    print(f"jarvis {__version__}")
    print(f"Model profile: {config.model_profile}")
    print(f"Primary model: {config.primary_model}")
    print(f"Ollama host: {config.ollama_host}")

    try:
        wait_for_server(host=config.ollama_host, timeout=5)
        print("Ollama server: running")
    except OllamaNotReadyError:
        print("Ollama server: not reachable")
        print("  Fix: run ./scripts/setup.sh")
        ok = False

    if ok:
        missing = check_models(config.models, host=config.ollama_host)
        if missing:
            print(f"Models missing: {', '.join(missing)}")
            print("  Fix: run 'jarvis setup'")
            ok = False
        else:
            print(f"Models installed: {', '.join(config.models)}")

    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    kb = int(line.split()[1])
                    gb = kb / (1024 * 1024)
                    print(f"System RAM: {gb:.1f} GB")
                    break
    except OSError:
        pass

    if ok:
        print("All checks passed.")
        return 0

    print("Some checks failed.")
    return 1


def _cmd_run(_args: argparse.Namespace) -> int:
    config = load_config()
    missing = check_models(config.models, host=config.ollama_host)
    if missing:
        print(
            f"Missing models: {', '.join(missing)}. Run 'jarvis setup' first.",
            file=sys.stderr,
        )
        return 1

    print(f"jarvis is ready (profile: {config.model_profile}).")
    print("Home automation runtime is not implemented yet.")
    return 0


def main(argv: list[str] | None = None) -> int:
    load_dotenv()

    parser = argparse.ArgumentParser(prog="jarvis")
    parser.add_argument("--version", action="version", version=f"jarvis {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    setup_parser = subparsers.add_parser("setup", help="Download required Ollama models")
    setup_parser.set_defaults(func=_cmd_setup)

    doctor_parser = subparsers.add_parser("doctor", help="Verify Ollama and model setup")
    doctor_parser.set_defaults(func=_cmd_doctor)

    run_parser = subparsers.add_parser("run", help="Start the jarvis application")
    run_parser.set_defaults(func=_cmd_run)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
