from typing import Dict, Any

from aiohttp import ClientSession, TCPConnector

from src.notifications.core.constants import DEFAULT_POOL_SETTNGS
from src.notifications.core.interface import NotificationInterface
from src.notifications.core.schemas import SessionPool, BaseResponse
from src.notifications.core.utils import send_with_retries_mechanism


class TelegramNotificationProcessor(NotificationInterface):
    def __init__(
            self,
            token: str,
            pool_settings: SessionPool = DEFAULT_POOL_SETTNGS
    ) -> None:
        self._notif_url: str = f"https://api.telegram.org/bot{token}/sendMessage"
        self._session_pool: ClientSession = ClientSession(
            connector=TCPConnector(
                **pool_settings.model_dump()
            )
        )

    async def send(
            self,
            text: str,
            chat_id: int,
            max_retries: int = 3
    ) -> BaseResponse:
        """
        Asynchronous sending a simple text message in Telegram via a bot

        Args:
            text (str): message
            chat_id (int): User ID in a private chat with the bot
            max_retries (int): number of retries in case of failure

        return: BaseResponse(
            status_code: general response code from the operation
            details: operation details. Example: {"ok": True, "result": {...}}
            execute_status: the overall status of the operation, true or false
        )
        """
        payload: Dict[str, Any] = {"chat_id": chat_id, "text": text}

        return await send_with_retries_mechanism(
            url=self._notif_url,
            payload_marker="json",  # <session>.post(json=...)
            payload=payload,
            max_retries=max_retries,
            session_pool=self._session_pool
        )

    async def close_session(self):
        await self._session_pool.close()
