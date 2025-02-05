from typing import Literal

from pydantic import BaseModel
from typing_extensions import Self

PasswordAlgorithm = Literal[
    "bcrypt",
    "argon2",
    "pbkdf2_sha256",
    "pbkdf2_sha512",
    "sha256_crypt",
    "sha512_crypt",
    "md5_crypt",
    "des_crypt",
]


class AuthConfig(BaseModel):
    """
    Configuration for the authentication system.

    Attributes:
        secret_key: The secret key for the authentication system.
        algorithm: The algorithm for the authentication system.
        access_token_expire_minutes: The number of minutes the access token is valid for.
    """

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    password_algorithm: PasswordAlgorithm

    @classmethod
    def from_json(cls, json_path: str) -> Self:
        with open(json_path, encoding="utf-8") as f:
            from json import load

            config = load(f)
        return cls(**config)
