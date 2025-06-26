class SearchEngineError(Exception):
    """Базовый обработчик ошибок для IncomingVoiceSearchEngine."""

    def __init__(self, message: str, code: int | str = "base-code-error") -> None:
        super().__init__(message)
        self.message = message
        self.code = code

    def __str__(self) -> str:
        if self.code:
            return f"[Error {self.code}]: {self.message}"

        return f"[Error]: {self.message}"
