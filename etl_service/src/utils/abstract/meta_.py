class SingletonMeta(type):
    """Meta-класс для паттерна Singleton."""

    instances_: dict = {}

    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        if cls not in cls.instances_.keys():
            cls.instances_[cls] = instance

        return cls.instances_[cls]
