from datetime import timedelta
from functools import cached_property
from typing import Any

from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from ..utils.auth.passlib import PasslibUtils
from .config import AuthConfig
from .schema import TokenData


class Auth:
    def __init__(self, config: AuthConfig, token_url: str, scopes: dict[str, str]):
        self.config = config
        self.token_url = token_url
        self.scopes = scopes

    @cached_property
    def oauth2_scheme(self) -> OAuth2PasswordBearer:
        return OAuth2PasswordBearer(tokenUrl=self.token_url, scopes=self.scopes)

    @cached_property
    def password_context(self) -> CryptContext:
        return PasslibUtils.get_password_context(self.config.password_algorithm)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        return PasslibUtils.verify_string(
            self.password_context, password, hashed_password
        )

    def hash_password(self, password: str) -> str:
        return PasslibUtils.hash_string(self.password_context, password)

    def encode_token(self, payload: dict[str, Any]) -> str:
        from ..utils.auth.jwt import JWTUtils

        return JWTUtils.encode_token(
            payload, self.config.secret_key, [self.config.algorithm]
        )

    def decode_token(self, token: str) -> dict[str, Any]:
        from ..utils.auth.jwt import JWTUtils

        return JWTUtils.decode_token(
            token, self.config.secret_key, algorithms=[self.config.algorithm]
        )

    def create_access_token(
        self,
        data: TokenData,
        expires_delta: timedelta | None = None,
    ) -> str:
        from datetime import datetime, timezone

        to_encode = data.model_dump()

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})

        return self.encode_token(to_encode)

    def is_required_scope(
        self,
        user_scopes: list[str],
        required_scopes: list[str],
    ) -> bool:
        """
        user攜帶的scope 是否符合端點的scope

        Args:
            user_scopes (list[str]): 使用者攜帶的scope
            required_scopes (list[str]): 端點要求的scope

        Returns:
            bool: 使用者攜帶的scope是否符合端點要求的scope
        """
        user_scopes_set = set(user_scopes)
        required_scopes_set = set(required_scopes)

        return user_scopes_set.issuperset(required_scopes_set)
