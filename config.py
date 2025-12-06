# config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Path to the .env file (same folder as this config.py)
ENV_PATH = Path(__file__).resolve().parent / ".env"

# Load the .env file
load_dotenv(ENV_PATH)

# Read environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TEMP_DIR = os.getenv("TEMP_DIR", "tmp_reports")
ENVIRONMENT = os.getenv("ENVIRONMENT", "local")
