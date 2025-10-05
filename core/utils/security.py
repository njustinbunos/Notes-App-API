from passlib.context import CryptContext
import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def generate_reset_token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)


def generate_verification_code(length: int = 6) -> str:
    return ''.join([str(secrets.randbelow(10)) for _ in range(length)])


def generate_api_key(length: int = 32) -> str:
    return secrets.token_hex(length)

