import sys

from db.migrations import run_database_migrations
from logging_config import configure_logging

logger = configure_logging()

if __name__ == "__main__":
    try:
        run_database_migrations()
    except Exception as exc:
        logger.exception("CropConnect MongoDB migration failed: %s", exc)
        sys.exit(1)
    logger.info("CropConnect MongoDB migrations completed.")
