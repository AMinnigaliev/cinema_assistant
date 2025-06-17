from abc import ABC, abstractmethod


class BaseStorage(ABC):

    @abstractmethod
    async def save_state(self, key_: str, value) -> None:
        pass

    @abstractmethod
    async def retrieve_state(self, key_: str):
        pass
