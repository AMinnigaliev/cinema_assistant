import requests
from requests.status_codes import codes

from settings import config
from testdata import AuthHeaders, Token, UserResponse, UserRoleEnum


def test_assign_user_role(
    create_users_and_login_superuser_f: tuple[UserResponse, Token]
) -> None:
    """Тест: назначение роли пользователю."""
    created_user_data, superuser_token_data = (
        create_users_and_login_superuser_f
    )

    url_ = (
        f"{config.auth_service_url}/api/v1/auth/users_role/"
        f"{created_user_data.id}/assign-role/{UserRoleEnum.ADMIN.value}"
    )
    headers_ = AuthHeaders(
        Authorization=f"Bearer {superuser_token_data.access_token}"
    ).model_dump()

    response_ = requests.post(url=url_, headers=headers_)
    status_code = response_.status_code

    assert status_code == codes.OK

    updated_role_user_data = UserResponse(**response_.json())
    assert updated_role_user_data.id == created_user_data.id
    assert updated_role_user_data.role == UserRoleEnum.ADMIN
    assert updated_role_user_data.role != created_user_data.role
