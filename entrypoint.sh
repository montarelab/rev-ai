#!/bin/bash

# Set default values for environment variables
export OLLAMA_URL=${OLLAMA_URL:-"http://localhost:11434"}
export OLLAMA_MODEL=${OLLAMA_MODEL:-"llama3.2"}
export LOGS_DIR=${LOGS_DIR:-"/app/logs"}

# Ensure logs directory exists
mkdir -p "${LOGS_DIR}"

# If no arguments provided, show help
if [ $# -eq 0 ]; then
    python main.py --help
    exit 0
fi

# Run the main application with provided arguments
exec python main.py "$@"
