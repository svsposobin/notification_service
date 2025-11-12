from typing import Dict, Any

from aiohttp import ClientSession, TCPConnector

from src.notifications.core.constants import DEFAULT_POOL_SETTNGS
from src.notifications.core.interface import NotificationInterface
from src.notifications.core.schemas import SessionPool, BaseResponse
from src.notifications.core.utils import send_with_retries_mechanism


class SMSNotificationProcessor(NotificationInterface):
    def __init__(
            self,
            token: str,
            pool_settings: SessionPool = DEFAULT_POOL_SETTNGS
    ) -> None:
        self._token = token
        self._notif_url: str = "https://sms.ru/sms/send"
        self._session_pool: ClientSession = ClientSession(
            connector=TCPConnector(
                **pool_settings.model_dump()
            )
        )

    async def send(
            self,
            text: str,
            phone_number: str,
            max_retries: int = 3
    ) -> BaseResponse:
        """
        Asynchronous SMS-"sendler" via sms.ru

        Args:
            text (str): message
            phone_number (str): What number should I send the message to?
            max_retries (int): number of retries in case of failure

        return: BaseResponse(
            status_code: general response code from the operation
            details: operation details. Example: {"ok": True, "result": {...}}
            execute_status: the overall status of the operation, true or false
        )
        """
        payload: Dict[str, Any] = {
            "api_id": self._token,
            "to": phone_number,
            "msg": text,
            "json": 1,  # Get the response in JSON
        }

        return await send_with_retries_mechanism(
            url=self._notif_url,
            payload_marker="data",  # <session>.post(data=...)
            payload=payload,
            max_retries=max_retries,
            session_pool=self._session_pool
        )

    async def close_session(self):
        await self._session_pool.close()
