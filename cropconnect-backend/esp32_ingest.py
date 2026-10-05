# Backwards-compatible ASGI entrypoint for deployments still targeting esp32_ingest:app.
import sys

import security_crypto
from app import app
from config import settings
from db import migrations as db_migrations
from db.mongodb import get_database
from logging_config import configure_logging
from security_crypto import encrypt_text
from services.esp32_service import esp32_key_hash

security_crypto.require_data_secret()

logger = configure_logging()


def run_database_migrations() -> None:
    db_migrations.run_database_migrations(get_database())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
