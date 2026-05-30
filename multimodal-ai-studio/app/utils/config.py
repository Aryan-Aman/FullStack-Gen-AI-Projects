"""
config.py - Configuration loader for API keys.

This module reads API keys from a .env file using python-dotenv
and provides simple getter functions for each key.
"""

import os
from dotenv import load_dotenv

# Load environment variables from the .env file into os.environ.
# This looks for a .env file in the project root directory.
load_dotenv()


def get_gemini_api_key():
    """
    Returns the Gemini API key from environment variables.
    Returns None if the key is not set or is empty.
    """
    key = os.getenv("GEMINI_API_KEY")
    return key if key else None


def get_hf_token():
    """
    Returns the Hugging Face API token from environment variables.
    Returns None if the token is not set or is empty.
    """
    token = os.getenv("HF_TOKEN")
    return token if token else None


def get_openrouter_api_key():
    """
    Returns the OpenRouter API key from environment variables.
    Returns None if the key is not set or is empty.
    """
    key = os.getenv("OPENROUTER_API_KEY")
    return key if key else None
