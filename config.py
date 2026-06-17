import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

SUB_PRICE = int(os.getenv("SUB_PRICE", "99"))
SUB_DAYS = int(os.getenv("SUB_DAYS", "30"))

FREE_VARIANTS = int(os.getenv("FREE_VARIANTS", "1"))
FREE_PRACTICE = int(os.getenv("FREE_PRACTICE", "3"))

DB_PATH = os.getenv("DB_PATH", "ege.db")
