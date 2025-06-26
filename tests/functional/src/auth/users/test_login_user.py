import requests
from requests.status_codes import codes

from src.auth.helpers import assert_valid_jwt
from testdata import Token, UserCreateRequest
from utils.custom_exceptions import FixtureError


def test_login_user(
    create_and_login_user_f: requests.Response,
    create_user_data_request_f: UserCreateRequest,
) -> None:
    """Тест: Логин пользователя."""
    if not create_and_login_user_f.status_code == codes.OK:
        raise FixtureError(
            f"User not login: {create_and_login_user_f.status_code}"
        )
    token_data = Token(**create_and_login_user_f.json())

    assert_valid_jwt(token_data)
