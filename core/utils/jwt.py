import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

import jwt 

_DEFAULT_TEST_SECRET = "test-secret-key"

def get_secret_key() -> str:
    key = os.getenv("JWT_SECRET_KEY", _DEFAULT_TEST_SECRET)
    if isinstance(key, bytes):
        try:
            key = key.decode("utf-8")
        except Exception:
            key = str(key)
    if key is None:
        key = _DEFAULT_TEST_SECRET
    if not isinstance(key, str):
        key = str(key)
    if key == "":
        raise RuntimeError("JWT_SECRET_KEY must be a non-empty string")
    return key

SECRET_KEY: str = get_secret_key()
ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


def _now_ts() -> int:
    return int(datetime.now(timezone.utc).timestamp())


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token. `data` must be JSON-serializable (strings/ints).
    `exp` and `iat` stored as integer epoch seconds.
    """
    to_encode = data.copy()
    now_ts = _now_ts()

    if expires_delta:
        expire_ts = int((datetime.now(timezone.utc) + expires_delta).timestamp())
    else:
        expire_ts = now_ts + int(ACCESS_TOKEN_EXPIRE_MINUTES * 60)

    to_encode.update({
        "exp": expire_ts,
        "iat": now_ts,
        "type": "access"
    })

    encoded = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    # PyJWT >=2 returns a str; older versions might return bytes — ensure str.
    if isinstance(encoded, bytes):
        encoded = encoded.decode("utf-8")
    return encoded


def create_refresh_token(data: Dict[str, Any]) -> str:
    to_encode = data.copy()
    now_ts = _now_ts()
    expire_ts = now_ts + int(REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60)

    to_encode.update({
        "exp": expire_ts,
        "iat": now_ts,
        "type": "refresh"
    })

    encoded = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    if isinstance(encoded, bytes):
        encoded = encoded.decode("utf-8")
    return encoded


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def verify_token_type(token: str, expected_type: str) -> bool:
    payload = decode_token(token)
    if not payload:
        return False
    return payload.get("type") == expected_type


def get_token_expiration(token: str) -> Optional[datetime]:
    payload = decode_token(token)
    if not payload:
        return None
    exp_timestamp = payload.get("exp")
    if exp_timestamp is None:
        return None
    if isinstance(exp_timestamp, (int, float)):
        return datetime.fromtimestamp(int(exp_timestamp), tz=timezone.utc)
    if isinstance(exp_timestamp, str) and exp_timestamp.isdigit():
        return datetime.fromtimestamp(int(exp_timestamp), tz=timezone.utc)
    try:
        return datetime.fromisoformat(exp_timestamp)
    except Exception:
        return None


def create_token_pair(user_data: Dict[str, Any]) -> Dict[str, str]:
    return {
        "access_token": create_access_token(user_data),
        "refresh_token": create_refresh_token(user_data),
        "token_type": "bearer"
    }
