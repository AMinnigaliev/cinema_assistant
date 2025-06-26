import time
import uuid

import pytest
from jose import JWTError, jwt

from settings import config
from testdata import Token


def assert_valid_jwt(token_data: Token) -> None:
    """Общая проверка формата JWT."""
    assert token_data.token_type == "bearer", "token_type is not 'bearer'"

    for name, raw_token in (
            ("access", token_data.access_token),
            ("refresh", token_data.refresh_token),
    ):
        parts = raw_token.split(".")
        assert len(parts) == 3, (
            f"Incorrect form {name}_token: expected 3 parts separated by "
            f"a dot, received {len(parts)}"
        )

        try:
            payload = jwt.decode(
                raw_token,
                config.secret_key,
                algorithms=[config.algorithm],
            )
        except JWTError as e:
            pytest.fail(f"{name}_token not valid as JWT: {e}")

        else:
            assert "exp" in payload, f"In {name}_token no exp"
            exp = payload["exp"]
            assert isinstance(exp, (int, float)), (
                f"CLAIM exp в JWT содержит нечисловое значение: "
                f"{exp!r}"
            )
            assert exp > time.time(), (
                f"{name}_token already expired (exp={exp})"
            )

            assert "user_id" in payload, f"There is no user_id in {name}_token"
            user_id = payload["user_id"]
            try:
                uuid.UUID(user_id)

            except (ValueError, AttributeError):
                pytest.fail(
                    f"user_id в {name}_token is not a UUID: "
                    f"{user_id}"
                )

            assert "role" in payload, f"There is no role in {name}_token"
            role = payload["role"]
            assert role == "user", (
                f"Invalid role in {name}_token: {role}"
            )