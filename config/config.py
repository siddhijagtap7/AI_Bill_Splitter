import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"

def load_config():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"config.json not found at {CONFIG_PATH}")

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


CONFIG = load_config()
local_tesseract_path = CONFIG["tesseract_path"]["local_path"]
docker_tesseract_path = CONFIG["tesseract_path"]["docker_path"]

items_price_prompt = CONFIG["prompts"]["items_price_prompt"]
tax_total_prompt = CONFIG["prompts"]["tax_total_prompt"]