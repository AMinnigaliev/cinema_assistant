import pytest

from testdata import UserLogoutResponse, UserUpdateRequest


@pytest.fixture
def update_user_data_request_f() -> UserUpdateRequest:
    return (
        UserUpdateRequest(
            first_name="first_name_test",
            last_name="last_name_update_test",
            password="password_test",
        )
    )


@pytest.fixture
def user_logout_data_response_f() -> UserLogoutResponse:
    return UserLogoutResponse(message="Successfully logged out")
