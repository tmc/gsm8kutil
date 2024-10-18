#!/usr/bin/env bash
# run-cgpt.sh - A script to run cgpt via promptfoo.
#
# promptfoo invokes with 3 args:
# 1. The prompt string
# 2. Config provided for this 'provider'
# 3. The structured information about the prompt.
set -euo pipefail

# send stderr to log file:
# exec 2> >(tee -a "/tmp/run-cgpt.log")
# set -x
# PS4='>> command: '

PROMPT="$1"
CONFIG="$2"

# Use jq to extract values with default fallbacks
BACKEND=$(jq -r '.config.backend // "ollama"' <<< "$CONFIG")
MODEL=$(jq -r '.config.model // "llama3.2:1b"' <<< "$CONFIG")
SYSTEM_PROMPT=$(jq -r '.config.system_prompt // empty' <<< "$CONFIG")
PREFILL=$(jq -r '.config.prefill // empty' <<< "$CONFIG")
MAX_TOKENS=$(jq -r '.config.max_tokens // 4096' <<< "$CONFIG")

echo "Running cgpt with backend: $BACKEND, model: $MODEL, system_prompt: $SYSTEM_PROMPT, prefill: $PREFILL"

cgpt \
		-b "$BACKEND" -m "$MODEL" \
		-s "$SYSTEM_PROMPT" -p "$PREFILL" \
		-t "$MAX_TOKENS" \
		-i "$PROMPT"
