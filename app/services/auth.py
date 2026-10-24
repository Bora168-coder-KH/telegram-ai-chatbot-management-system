"""Admin passwords, roles and permissions.

Passwords are hashed with scrypt (Python standard library), never stored as text.
"""
import hashlib
import hmac
import secrets

PERMISSIONS = ["view", "create", "edit", "delete", "reply", "broadcast", "train", "report"]

_N, _R, _P = 2**14, 8, 1


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=_N, r=_R, p=_P)
    return f"scrypt${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, salt, digest = stored.split("$")
    except ValueError:
        return False
    if scheme != "scrypt":
        return False
    check = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=_N, r=_R, p=_P)
    return hmac.compare_digest(check.hex(), digest)
