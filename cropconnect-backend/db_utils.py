import re


def quote_identifier(name: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_-]+", name or ""):
        raise ValueError(f"Unsafe identifier: {name!r}")
    return f"`{name}`"