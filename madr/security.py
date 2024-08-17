from pwdlib import PasswordHash

pwd_context = PasswordHash.recommended()


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hash_password: str) -> bool:
    return pwd_context.verify(password, hash_password)
