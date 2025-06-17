from enum import Enum


class UserRoleEnum(str, Enum):
    USER = "user"
    ADMIN = "admin"
    SUPERUSER = "superuser"

    @classmethod
    def get_all_roles(cls) -> list[str]:
        """
        Возвращает список всех значений ролей, определённых в перечислении.
        """
        return [role.strip() for role in cls]
