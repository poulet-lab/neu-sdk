from re import match

from bcrypt import checkpw, gensalt, hashpw

KIND = {"session": 0, "api": 1}
SALT = gensalt()


def password_strength(password):
    if not match(
        r"^.*(?=.{8})(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@£$%^&*()_+={}?:~\[\]])[a-zA-Z0-9!@£$%^&*()_+={}?:~\[\]]+$",
        password,
    ):
        raise ValueError(
            "Password must be at least 8 characters long and include at least one number, one lowercase letter, one uppercase letter, and one special character."
        )
    return True


def encrypt_password(password: str) -> str:
    return hashpw(password.encode(), SALT).decode()


def check_password(password: str, hashed_password: str) -> bool:
    return checkpw(password.encode(), hashed_password.encode())
