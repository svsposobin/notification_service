from typing import Any, Dict
from asyncio import sleep as async_sleep

from aiohttp import ClientSession

from src.notifications.core.schemas import BaseResponse


async def send_with_retries_mechanism(
        url: str,
        payload_marker: str,
        payload: Dict[str, Any],
        max_retries: int,
        session_pool: ClientSession,
) -> BaseResponse:
    """
    Centralized management of notification sending with session pooling

    Args:
        url (str): URL to which the post request should be sent.
        payload_marker (str): What type of data should I send the payload with?.
            Example: payload_marker="json"  ... -> <session>.post(json=payload)
                     payload_marker="data" ... -> <session>.post(data=payload)
        payload (dict): All the necessary useful information for the request.
        max_retries (int): ...
        session_pool (ClientSession): The pool in the context of which requests will be made
    """
    result: BaseResponse = BaseResponse()
    request_params: Dict[str, Any] = {
        "url": url,
        payload_marker: payload,
    }

    for attempt in range(max_retries):
        try:
            async with session_pool.post(**request_params) as response:
                response_data: Any = await response.json()

                if response.ok:
                    result.status_code = response.status
                    result.details = response_data
                    result.execute_status = True

                    return result

                result.status_code = response.status
                result.details = response_data

                if 400 <= response.status < 500:  # Client errors
                    break

                await async_sleep(2 ** attempt)  # Exponential backoff-strategy

        except Exception as error:
            result.status_code = getattr(error, "status", 500)
            result.details = str(error)

            if attempt < max_retries - 1 and not (400 <= result.status_code < 500):
                await async_sleep(2 ** attempt)

    return result
