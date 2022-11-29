import os
from pathlib import Path


DATABASE_URL = os.environ.get("DATABASE_URL", "")
API_KEY = os.environ.get("API_KEY", "")
AUTH_DOMAIN = os.environ.get("AUTH_DOMAIN", "")
PROJECT_ID = os.environ.get("PROJECT_ID", "")
STORAGE_BUCKET = os.environ.get("STORAGE_BUCKET", "")
MESSAGE_SENDER_ID = os.environ.get("MESSAGE_SENDER_ID", "")
APP_ID = os.environ.get("APP_ID", "")
MEASUREMENT_ID = os.environ.get("MEASUREMENT_ID", "")


def apply_parameters(src: str, params: dict) -> str:
    for key, value in params.items():
        src = src.replace("%{" + key + "}", value)
    return src


C_EDITOR_SRC = Path("./c_editor.html").read_text()


C_EDITOR_HTML = apply_parameters(C_EDITOR_SRC, {
    "database_url": DATABASE_URL,
    "api_key": API_KEY,
    "auth_domain": AUTH_DOMAIN,
    "project_id": PROJECT_ID,
    "storage_bucket": STORAGE_BUCKET,
    "messaging_sender_id": MESSAGE_SENDER_ID,
    "app_id": APP_ID,
    "measurement_id": MEASUREMENT_ID,
})
