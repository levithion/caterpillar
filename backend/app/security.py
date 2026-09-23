import hashlib
import secrets

_ITERATIONS = 100_000


def hash_password(password: str, salt_hex: str | None = None) -> tuple[str, str]:
    """Returns (password_hash_hex, salt_hex). Generates a new random salt
    unless one is passed in (needed when re-deriving a hash to verify a
    login attempt against a stored salt)."""
    salt_hex = salt_hex or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), _ITERATIONS)
    return digest.hex(), salt_hex


def verify_password(password: str, salt_hex: str, expected_hash_hex: str) -> bool:
    computed_hash, _ = hash_password(password, salt_hex)
    return secrets.compare_digest(computed_hash, expected_hash_hex)
