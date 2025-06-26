import requests
from requests.status_codes import codes

from settings import config
from src.auth.helpers import assert_valid_jwt
from testdata import RefreshToken, Token, UserCreateRequest
from utils.custom_exceptions import FixtureError


def test_refresh_token_user(
    create_and_login_user_f: requests.Response,
    create_user_data_request_f: UserCreateRequest,
) -> None:
    """Тест: обновление refresh-токена."""
    if not create_and_login_user_f.status_code == codes.OK:
        raise FixtureError(
            f"User not login: {create_and_login_user_f.status_code}"
        )
    old_token_data = Token(**create_and_login_user_f.json())

    url_ = f"{config.auth_service_url}/api/v1/auth/users/refresh"
    payload_ = RefreshToken(
        refresh_token=old_token_data.refresh_token
    ).model_dump()

    response_ = requests.post(url=url_, params=payload_)
    status_code = response_.status_code

    assert status_code == requests.status_codes.codes.OK

    new_token_data = Token(**response_.json())

    assert new_token_data.access_token == old_token_data.access_token
    assert new_token_data.refresh_token == old_token_data.refresh_token

    assert_valid_jwt(new_token_data)
