import pytest
import requests
from requests.status_codes import codes
from sqlalchemy import Engine, text

from settings import config
from testdata import (Token, UserCreateRequest, UserLoginRequest, UserResponse,
                      UserRoleEnum)
from utils.custom_exceptions import FixtureError
from utils.pg_helpers import remove_user_db


@pytest.fixture
def create_superuser_data_request_f() -> UserCreateRequest:
    return (
        UserCreateRequest(
            first_name="first_name_superuser_test",
            last_name="last_name_superuser_test",
            login="login_superuser_test",
            password="password_superuser_test",
        )
    )


@pytest.fixture
def login_superuser_data_request_f() -> UserLoginRequest:
    return (
        UserLoginRequest(
            username="login_superuser_test",
            password="password_superuser_test",
        )
    )


@pytest.fixture(scope="function", autouse=True)
def remove_superuser_db_f(
    pg_engine: Engine, create_superuser_data_request_f: UserCreateRequest
) -> None:
    """Fixture: удаление суперпользователя из DB."""
    remove_user_db(create_superuser_data_request_f.login, pg_engine)

    yield

    # remove_user_db(create_superuser_data_request_f.login, pg_engine)


@pytest.fixture
def set_superuser_role_db_f(
    pg_engine: Engine, create_superuser_data_request_f: UserCreateRequest
) -> None:
    """Fixture: пользователю присваивается роль "суперпользователя" DB."""
    with pg_engine.connect() as conn:
        conn.execute(
            text(
                "UPDATE auth.users "
                "SET role = :role "
                "WHERE login = :login"
            ),
            {
                "role": UserRoleEnum.SUPERUSER.name,
                "login": create_superuser_data_request_f.login,
            },
        )
        conn.commit()


@pytest.fixture
def create_superuser_f(
    create_superuser_data_request_f: UserCreateRequest
) -> requests.Response:
    """Fixture: регистрация суперпользователя."""
    url_ = f"{config.auth_service_url}/api/v1/auth/users/register"
    payload_ = create_superuser_data_request_f.model_dump()

    return requests.post(url=url_, json=payload_)


@pytest.fixture
def create_and_login_superuser_f(
    create_superuser_f: requests.Response,
    login_superuser_data_request_f: UserLoginRequest,
    request,
) -> requests.Response:
    """Fixture: регистрация и авторизация суперпользователя."""
    if not create_superuser_f.status_code == codes.CREATED:
        raise FixtureError(
            f"User not created: {create_superuser_f.status_code}"
        )
    request.getfixturevalue("set_superuser_role_db_f")

    url_ = f"{config.auth_service_url}/api/v1/auth/users/login"
    payload_ = login_superuser_data_request_f.model_dump()

    return requests.post(url=url_, data=payload_)


@pytest.fixture
def create_users_and_login_superuser_f(
    create_user_f: requests.Response,
    create_and_login_superuser_f: requests.Response,
) -> tuple[UserResponse, Token]:
    if not create_user_f.status_code == codes.CREATED:
        raise FixtureError(
            f"User not created: {create_user_f.status_code}"
        )

    if not create_and_login_superuser_f.status_code == codes.OK:
        raise FixtureError(
            f"Superuser not login: "
            f"{create_and_login_superuser_f.status_code}"
        )

    created_user_data = UserResponse(**create_user_f.json())
    superuser_token_data = Token(**create_and_login_superuser_f.json())

    return created_user_data, superuser_token_data
