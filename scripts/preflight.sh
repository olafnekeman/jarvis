#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

OS="$(uname -s)"
ARCH="$(uname -m)"

case "$OS:$ARCH" in
  Linux:aarch64)
    PLATFORM="raspberry-pi"
    ;;
  Darwin:arm64|Darwin:x86_64)
    PLATFORM="macos"
    ;;
  *)
    echo "error: unsupported platform ${OS} (${ARCH})" >&2
    echo "  Supported: Raspberry Pi OS 64-bit (Linux aarch64), macOS (arm64 or x86_64)" >&2
    exit 1
    ;;
esac

echo "Platform: ${PLATFORM} (${OS} ${ARCH})"

TOTAL_KB=""
if [[ "$OS" == "Linux" ]] && command -v free >/dev/null 2>&1; then
  TOTAL_KB="$(free | awk '/^Mem:/ {print $2}')"
elif [[ "$OS" == "Darwin" ]] && command -v sysctl >/dev/null 2>&1; then
  if TOTAL_BYTES="$(sysctl -n hw.memsize 2>/dev/null)"; then
    TOTAL_KB="$((TOTAL_BYTES / 1024))"
  fi
fi

if [[ -n "$TOTAL_KB" ]]; then
  TOTAL_GB="$(awk "BEGIN {printf \"%.1f\", $TOTAL_KB / 1024 / 1024}")"
  echo "Detected RAM: ${TOTAL_GB} GB"

  if [[ -z "${JARVIS_MODEL_PROFILE:-}" ]]; then
    if awk "BEGIN {exit !($TOTAL_KB < 3500000)}"; then
      export JARVIS_MODEL_PROFILE="pi4_4gb"
      echo "Using pi4_4gb model profile (auto-detected)"
    elif awk "BEGIN {exit !($TOTAL_KB < 7500000)}"; then
      export JARVIS_MODEL_PROFILE="pi4_8gb"
      echo "Using pi4_8gb model profile (auto-detected)"
    else
      export JARVIS_MODEL_PROFILE="pi4_8gb"
      echo "Using pi4_8gb model profile (high-memory system)"
    fi
  else
    echo "Using model profile: ${JARVIS_MODEL_PROFILE} (from environment)"
  fi
elif [[ "$PLATFORM" == "macos" ]]; then
  export JARVIS_MODEL_PROFILE="${JARVIS_MODEL_PROFILE:-pi4_8gb}"
  echo "Using model profile: ${JARVIS_MODEL_PROFILE} (macOS default)"
fi

if command -v df >/dev/null 2>&1; then
  FREE_KB="$(df -k "$REPO_ROOT" | awk 'NR==2 {print $4}')"
  FREE_GB="$(awk "BEGIN {printf \"%.1f\", $FREE_KB / 1024 / 1024}")"
  echo "Free disk space: ${FREE_GB} GB"

  if awk "BEGIN {exit !($FREE_KB < 3145728)}"; then
    echo "error: need at least 3 GB free disk space for model downloads" >&2
    exit 1
  fi

  if [[ "$PLATFORM" == "raspberry-pi" ]]; then
    if [[ -f /proc/device-tree/model ]] && grep -qi "raspberry" /proc/device-tree/model 2>/dev/null; then
      ROOT_DEV="$(df "$REPO_ROOT" | awk 'NR==2 {print $1}')"
      if [[ "$ROOT_DEV" == *"mmcblk"* ]]; then
        echo "warning: running from microSD — model loads will be slow. An SSD is recommended."
      fi
    fi
  fi
fi

echo "Preflight checks passed."
