from __future__ import annotations
import bcrypt
import secrets
from typing import Optional
BCRYPT_ROUNDS = 12


def hash_password(password: str, rounds: int = BCRYPT_ROUNDS) -> str:
    if not isinstance(password, str) or password == "":
        raise ValueError("password must be a non-empty string")

    # bcrypt expects bytes
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds))
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not (isinstance(plain_password, str) and isinstance(hashed_password, str)):
        return False
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except (ValueError, TypeError):
        # If hashed_password is malformed or not bytes-decodable
        return False


def generate_reset_token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)


def generate_verification_code(length: int = 6) -> str:
    """Generate a numeric verification code (string) of given length."""
    if length <= 0:
        raise ValueError("length must be positive")
    return ''.join(str(secrets.randbelow(10)) for _ in range(length))


def generate_api_key(length: int = 32) -> str:
    if length <= 0:
        raise ValueError("length must be positive")
    return secrets.token_hex(length)
