"""MongoDB client and database helpers for CropConnect."""
from __future__ import annotations

from contextlib import contextmanager
from threading import Lock
from typing import Iterator

from pymongo import MongoClient
from pymongo.database import Database

from config import settings

_client: MongoClient | None = None
_client_lock = Lock()


def get_client() -> MongoClient:
    global _client
    if _client is None:
        with _client_lock:
            if _client is None:
                _client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)
    return _client


def get_database() -> Database:
    return get_client()[settings.mongodb_database]


@contextmanager
def database_context() -> Iterator[Database]:
    yield get_database()


def ping_database() -> None:
    get_client().admin.command("ping")


def close_client() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None
