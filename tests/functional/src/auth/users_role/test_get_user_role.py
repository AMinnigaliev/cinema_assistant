import requests

from settings import config
from testdata import (AuthHeaders, GetUserRoleResponse, Token, UserResponse,
                      UserRoleEnum)


def test_assign_user_role(
    create_users_and_login_superuser_f: tuple[UserResponse, Token]
) -> None:
    """Тест: получение роли суперпользователю."""
    created_user_data, superuser_token_data = (
        create_users_and_login_superuser_f
    )

    url_ = (
        f"{config.auth_service_url}/api/v1/auth/users_role/"
        f"{created_user_data.id}/role"
    )
    headers_ = AuthHeaders(
        Authorization=f"Bearer {superuser_token_data.access_token}"
    ).model_dump()

    response_ = requests.get(url=url_, headers=headers_)
    status_code = response_.status_code

    assert status_code == requests.status_codes.codes.OK

    user_role_response_data = GetUserRoleResponse(role=response_.json())
    assert user_role_response_data.role == UserRoleEnum.USER
