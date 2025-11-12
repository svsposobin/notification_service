from abc import ABC, abstractmethod
from typing import Any


class NotificationInterface(ABC):
    @abstractmethod
    async def send(self, *args: Any, **kwargs: Any):
        raise NotImplementedError()

    @abstractmethod
    async def close_session(self):
        """
            Closing the session pool to enable integration into other services
        """
        raise NotImplementedError()
