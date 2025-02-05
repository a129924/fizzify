from passlib.context import CryptContext

from ...auth.config import PasswordAlgorithm


class PasslibUtils:
    """
    Utility class for using passlib.
    """

    @classmethod
    def get_password_context(
        cls,
        algorithm: PasswordAlgorithm,
    ) -> CryptContext:
        """
        Get a password context for the given algorithm.

        Args:
            algorithm: The algorithm to use for the password context.

        Returns:
            A password context for the given algorithm.
        """
        return CryptContext(schemes=[algorithm], deprecated="auto")

    @classmethod
    def hash_string(
        cls,
        password_context: CryptContext,
        password: str,
    ) -> str:
        """
        Hash a string using the given password context.

        Args:
            password_context: The password context to use for the hash.
            password: The string to hash.

        Returns:
            The hashed string.
        """
        return password_context.hash(password)

    @classmethod
    def verify_string(
        cls,
        password_context: CryptContext,
        password: str,
        hashed_password: str,
    ) -> bool:
        """
        Verify a string against a hashed password using the given password context.

        Args:
            password_context: The password context to use for the verification.
            password: The string to verify.
            hashed_password: The hashed password to verify against.

        Returns:
            True if the string is verified against the hashed password, False otherwise.
        """
        return password_context.verify(password, hashed_password)
