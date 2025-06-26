class FixtureError(Exception):
    """Exception при ошибке в работе fixture."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
