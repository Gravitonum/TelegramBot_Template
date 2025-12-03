#!/usr/bin/env python3
"""
Script to list available LLM models from Ollama server.
Reads configuration from .env file.
"""

import os
import requests
from dotenv import load_dotenv


def load_ollama_config():
    """Load Ollama configuration from .env file"""
    load_dotenv()

    ollama_url = os.getenv("OLLAMA_URL")
    ollama_model = os.getenv("OLLAMA_MODEL")

    if not ollama_url:
        raise ValueError("OLLAMA_URL not found in .env file")

    return ollama_url, ollama_model


def list_ollama_models(ollama_url):
    """List available models from Ollama server"""
    try:
        response = requests.get(f"{ollama_url}/api/tags")
        response.raise_for_status()
        return response.json().get("models", [])
    except requests.RequestException as e:
        print(f"Error connecting to Ollama server: {e}")
        return []


def main():
    """Main function to list LLM models"""
    try:
        # Load configuration
        ollama_url, current_model = load_ollama_config()
        print(f"Ollama URL: {ollama_url}")
        print(f"Current Model: {current_model}")
        print("\nFetching available models...\n")

        # List available models
        models = list_ollama_models(ollama_url)

        if not models:
            print("No models found or unable to connect to Ollama server.")
            return

        # Display models in a nice format
        print("Available LLM Models:")
        print("-" * 50)
        for model in models:
            name = model.get("name", "Unknown")
            size = model.get("size", 0)
            modified_at = model.get("modified_at", "Unknown")
            print(f"Name: {name}")
            print(f"Size: {size} bytes")
            print(f"Modified: {modified_at}")
            print("-" * 50)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
