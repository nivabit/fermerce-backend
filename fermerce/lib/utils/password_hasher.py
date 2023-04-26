from passlib import context

pwd_context = context.CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hasher:
    @staticmethod
    def hash_password(plaintext_password: str) -> bytes:
        password = pwd_context.hash(plaintext_password)
        if password:
            return password
        return None

    @staticmethod
    def check_password(plaintext_password: str, hashed_password: bytes) -> bool:
        password = pwd_context.verify(plaintext_password, hashed_password)
        if password:
            return True
        return False
