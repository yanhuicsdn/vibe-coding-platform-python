"""
Security utilities - password hashing, JWT tokens, etc.
"""

from datetime import datetime, timedelta
from typing import Any

import jwt
from passlib.context import CryptContext


class PasswordHandler:
    """Password hashing and verification using bcrypt"""

    def __init__(self):
        self.context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash(self, password: str) -> str:
        """Hash a password"""
        return self.context.hash(password)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash"""
        return self.context.verify(plain_password, hashed_password)

    def validate_strength(self, password: str) -> tuple[bool, list[str]]:
        """
        Validate password strength

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")

        if not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")

        if not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")

        if not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")

        return (len(errors) == 0, errors)


class JWTHandler:
    """JWT token generation and verification"""

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def create_access_token(
        self,
        data: dict[str, Any],
        expires_delta: timedelta | None = None,
    ) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=30)

        to_encode.update({"exp": expire, "iat": datetime.utcnow()})

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def decode_token(self, token: str) -> dict[str, Any]:
        """Decode and verify a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationException("Token has expired")
        except jwt.JWTError as e:
            raise AuthenticationException(f"Invalid token: {str(e)}")

    def create_hasura_claims(
        self,
        user_id: str,
        tenant_id: str,
        project_id: str | None = None,
        default_role: str = "user",
        allowed_roles: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Create Hasura JWT claims

        Args:
            user_id: User ID
            tenant_id: Tenant ID
            project_id: Project ID (optional)
            default_role: Default role for the user
            allowed_roles: List of allowed roles

        Returns:
            Dictionary with Hasura-compatible JWT claims
        """
        if allowed_roles is None:
            allowed_roles = ["user"]

        claims = {
            "sub": user_id,
            "https://hasura.io/jwt/claims": {
                "x-hasura-user-id": user_id,
                "x-hasura-tenant-id": tenant_id,
                "x-hasura-default-role": default_role,
                "x-hasura-allowed-roles": allowed_roles,
            },
        }

        if project_id:
            claims["https://hasura.io/jwt/claims"]["x-hasura-project-id"] = project_id

        return claims
