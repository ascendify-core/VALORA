from database import add_user, get_user
import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username: str, password: str, profession: str = "Individual", account_type: str = "Individual") -> bool:
    hashed = hash_password(password)
    return add_user(username, hashed, profession, account_type)

def validate_user(username: str, password: str) -> bool:
    user = get_user(username)
    if not user:
        return False
    stored_username, stored_password, *_ = user
    return stored_password == hash_password(password)
