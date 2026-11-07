from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
APP_NAME = os.getenv("APP_NAME", "Recruta Cidadão")
