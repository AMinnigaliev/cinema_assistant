import requests
from requests.status_codes import codes

from settings import config
from testdata import AuthHeaders, Token, UserResponse, UserUpdateRequest
from utils.custom_exceptions import FixtureError


def test_update_user(
    create_and_login_user_f: requests.Response,
    update_user_data_request_f: UserUpdateRequest,
) -> None:
    """Тест: обновление данных пользователя."""
    if not create_and_login_user_f.status_code == codes.OK:
        raise FixtureError(
            f"User not login: {create_and_login_user_f.status_code}"
        )
    token_data = Token(**create_and_login_user_f.json())

    url_ = f"{config.auth_service_url}/api/v1/auth/users/update"
    payload_ = update_user_data_request_f.model_dump()
    headers_ = AuthHeaders(
        Authorization=f"Bearer {token_data.access_token}"
    ).model_dump()

    response_ = requests.patch(url=url_, json=payload_, headers=headers_)
    status_code = response_.status_code

    assert status_code == codes.OK

    updated_user_data = UserResponse(**response_.json())
    assert (updated_user_data.first_name ==
            update_user_data_request_f.first_name)
    assert (updated_user_data.last_name ==
            update_user_data_request_f.last_name)
