"""
Configuration settings for Melody2Music
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"

# Model settings
MODEL_SIZE = os.getenv("MODEL_SIZE", "melody")  # small, medium, large, melody
TARGET_SAMPLE_RATE = int(os.getenv("TARGET_SAMPLE_RATE", "16000"))

# Server settings
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# Generation defaults
DEFAULT_DURATION = float(os.getenv("DEFAULT_DURATION", "10.0"))
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "1.0"))
DEFAULT_CFG_COEF = float(os.getenv("DEFAULT_CFG_COEF", "3.0"))
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "250"))

# Processing limits
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "wav,mp3,ogg,flac,m4a").split(",")

# Device
DEVICE = os.getenv("DEVICE", "")  # Empty string for auto-detection

# CREPE settings
CREPE_MODEL = "full"  # full, large, medium, small, tiny
CREPE_HOP_LENGTH = 160  # ~10ms for 16kHz
CREPE_FMIN = 50  # Minimum frequency (Hz)
CREPE_FMAX = 800  # Maximum frequency for humming (Hz)
CREPE_CONFIDENCE_THRESHOLD = 0.5

# Ensure directories exist
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

