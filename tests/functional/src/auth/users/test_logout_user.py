import requests
from requests.status_codes import codes

from settings import config
from testdata import AuthHeaders, Token, UserLogoutRequest, UserLogoutResponse
from utils.custom_exceptions import FixtureError


def test_logout_user(
    create_and_login_user_f: requests.Response,
    user_logout_data_response_f: UserLogoutResponse,
) -> None:
    """Тест: выход пользователя из системы."""
    if not create_and_login_user_f.status_code == codes.OK:
        raise FixtureError(
            f"User not login: {create_and_login_user_f.status_code}"
        )
    token_data = Token(**create_and_login_user_f.json())

    url_ = f"{config.auth_service_url}/api/v1/auth/users/logout"
    payload_ = UserLogoutRequest(
        refresh_token=token_data.refresh_token
    ).model_dump()
    headers_ = AuthHeaders(
        Authorization=f"Bearer {token_data.access_token}"
    ).model_dump()

    response_ = requests.post(url=url_, params=payload_, headers=headers_)
    status_code = response_.status_code

    assert status_code == requests.status_codes.codes.OK

    user_logout_data = UserLogoutResponse(**response_.json())
    assert user_logout_data.message == user_logout_data_response_f.message
