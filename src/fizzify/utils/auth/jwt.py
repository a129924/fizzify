from jwt import decode, encode


class JWTUtils:
    @staticmethod
    def decode_token(
        token: str,
        jwt_secret: str,
        algorithms: list[str],
    ) -> dict:
        """
        Decode a JWT token.

        Args:
            token (str): The JWT token to decode.
            jwt_secret (str): The secret key used to encode the token.
            algorithms (list[str]): The algorithms to use for decoding.

        Returns:
            dict: The decoded token payload.
        """
        return decode(token, jwt_secret, algorithms=algorithms)

    @staticmethod
    def encode_token(
        payload: dict,
        jwt_secret: str,
        algorithms: list[str],
    ) -> str:
        """
        Encode a JWT token.

        Args:
            payload (dict): The payload to encode.
            jwt_secret (str): The secret key used to encode the token.
            algorithms (list[str]): The algorithms to use for encoding.

        Returns:
            str: The encoded JWT token.
        """
        return encode(payload, jwt_secret, algorithm=algorithms[0])
