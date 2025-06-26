import pytest
import requests
from requests.status_codes import codes
from sqlalchemy import Engine

from settings import config
from testdata import UserCreateRequest, UserLoginRequest
from utils.custom_exceptions import FixtureError
from utils.pg_helpers import remove_user_db


@pytest.fixture
def create_user_data_request_f() -> UserCreateRequest:
    return (
        UserCreateRequest(
            first_name="first_name_test",
            last_name="last_name_test",
            login="login_test",
            password="password_test",
        )
    )


@pytest.fixture
def login_user_data_request_f() -> UserLoginRequest:
    return (
        UserLoginRequest(
            username="login_test",
            password="password_test",
        )
    )


@pytest.fixture
def create_user_f(
    create_user_data_request_f: UserCreateRequest
) -> requests.Response:
    """Fixture: регистрация пользователя."""
    url_ = f"{config.auth_service_url}/api/v1/auth/users/register"
    payload_ = create_user_data_request_f.model_dump()

    return requests.post(url=url_, json=payload_)


@pytest.fixture
def create_and_login_user_f(
    create_user_f: requests.Response,
    login_user_data_request_f: UserLoginRequest,
) -> requests.Response:
    """Fixture: регистрация и авторизация пользователя."""
    if not create_user_f.status_code == codes.CREATED:
        raise FixtureError(f"User not created: {create_user_f.status_code}")

    url_ = f"{config.auth_service_url}/api/v1/auth/users/login"
    payload_ = login_user_data_request_f.model_dump()

    return requests.post(url=url_, data=payload_)


@pytest.fixture(scope="function", autouse=True)
def remove_user_db_f(pg_engine: Engine, create_user_data_request_f):
    """
    Всегда перед тестом удаляем login_test (на случай,
    если он остался от предыдущего запуска),
    а после теста — снова.
    """
    remove_user_db(create_user_data_request_f.login, pg_engine)

    yield

    remove_user_db(create_user_data_request_f.login, pg_engine)
