import requests
from requests.status_codes import codes

from testdata import UserCreateRequest, UserResponse


def test_register_user(
    create_user_data_request_f: UserCreateRequest,
    create_user_f: requests.Response,
) -> None:
    """Тест: регистрация пользователя."""
    response_ = create_user_f
    status_code = response_.status_code

    assert status_code == codes.CREATED, (
        f"Users not register: {status_code}"
    )

    created_user_data = UserResponse(**response_.json())
    assert created_user_data.id is not None
    assert (created_user_data.first_name ==
            create_user_data_request_f.first_name)
    assert (created_user_data.last_name ==
            create_user_data_request_f.last_name)
    assert created_user_data.role == "user"
