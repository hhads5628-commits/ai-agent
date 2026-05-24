import os


def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def get_env(name: str, default: str) -> str:
    return os.getenv(name, default)
