#!/bin/bash
# Check if the model is available and download it if not
MODEL_NAME="mistral:latest"
RESPONSE=$(curl -s http://localhost:11434/models)

if [[ $RESPONSE == *"$MODEL_NAME"* ]]; then
    echo "Model $MODEL_NAME is already available."
else
    echo "Downloading model $MODEL_NAME..."
    curl -X POST http://localhost:11434/models/$MODEL_NAME/download
fi
