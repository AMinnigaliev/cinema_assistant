class EntitiesNotFoundInDBError(Exception):
    """Обработчик ошибки - записи для сущности не найдены в БД."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class EventRuleError(Exception):
    """Обработчик ошибки - ошибка при обработке события по правилу."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
