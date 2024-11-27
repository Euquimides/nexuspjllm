#!/bin/bash

# Initialize Ollama
/bin/ollama serve &
# Store PID
pid=$!

# Pause to let Ollama start
sleep 5

echo "Downloading language model..."
# Download language model (using valid model name)
ollama pull llama2 || { echo "Failed to download llama2 model"; exit 1; }

# Download embedding model
echo "Downloading embedding model..."
ollama pull nomic-embed-text || { echo "Failed to download embedding model"; exit 1; }

echo "Language and embedding models downloaded successfully."

# Wait for Ollama process to finish
wait $pid