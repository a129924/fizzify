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
        """
        OAuth2PasswordBearer 是 FastAPI 提供的一個類別，用於處理 OAuth2 授權流程。
        它會在每次請求中檢查 Authorization 標頭，確保使用者已通過身份驗證。
        """
        return OAuth2PasswordBearer(tokenUrl=self.token_url, scopes=self.scopes)

    @cached_property
    def password_context(self) -> CryptContext:
        """
        密碼加密的 context
        """
        return PasslibUtils.get_password_context(self.config.password_algorithm)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        驗證密碼
        """
        return PasslibUtils.verify_string(
            self.password_context, password, hashed_password
        )

    def hash_password(self, password: str) -> str:
        """
        加密密碼

        Args:
            password (str): 要加密的密碼

        Returns:
            str: 加密後的密碼
        """
        return PasslibUtils.hash_string(self.password_context, password)

    def encode_token(self, payload: dict[str, Any]) -> str:
        """
        編碼 token

        Args:
            payload (dict[str, Any]): 要編碼的 payload

        Returns:
            str: 編碼後的 token
        """
        from ..utils.auth.jwt import JWTUtils

        return JWTUtils.encode_token(
            payload, self.config.secret_key, [self.config.algorithm]
        )

    def decode_token(self, token: str) -> TokenData:
        """
        解碼 token

        Args:
            token (str): 要解碼的 token

        Returns:
            TokenData: 解碼後的 payload
        """
        from ..utils.auth.jwt import JWTUtils

        return TokenData(
            **JWTUtils.decode_token(
                token, self.config.secret_key, algorithms=[self.config.algorithm]
            )
        )

    def create_access_token(
        self,
        data: TokenData,
        expires_delta: timedelta | None = None,
    ) -> str:
        """
        創建 access token

        Args:
            data (TokenData): 要創建的 token 的 payload
            expires_delta (timedelta | None): 過期時間

        Returns:
            str: 創建後的 token
        """
        from datetime import datetime, timezone

        to_encode = data.model_dump()

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)

        to_encode.update({"expired_at": expire})

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
