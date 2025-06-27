import requests
from requests.status_codes import codes

from settings import config
from testdata import AuthHeaders, Token, UserHistoryResponse
from utils.custom_exceptions import FixtureError


def test_history_user(
    create_and_login_user_f: requests.Response,
) -> None:
    """Тест: получение истории входа пользователя."""
    if not create_and_login_user_f.status_code == codes.OK:
        raise FixtureError(
            f"User not login: {create_and_login_user_f.status_code}"
        )
    token_data = Token(**create_and_login_user_f.json())

    url_ = f"{config.auth_service_url}/api/v1/auth/users/history"
    headers_ = AuthHeaders(
        Authorization=f"Bearer {token_data.access_token}"
    ).model_dump()

    response_ = requests.get(url=url_, headers=headers_)
    status_code = response_.status_code

    assert status_code == codes.OK

    user_login_history = [
        UserHistoryResponse(**res_lst) for res_lst in response_.json()
    ]
    assert len(user_login_history) == 1

    user_first_login_history = next(iter(user_login_history))
    assert user_first_login_history.user_id is not None
    assert user_first_login_history.login_time is not None
    assert user_first_login_history.user_agent is not None
