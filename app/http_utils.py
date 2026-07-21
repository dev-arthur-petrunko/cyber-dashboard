"""
requests.get(timeout=X) не защищает от сервера, который "капает" данные
мелкими порциями медленнее X секунд между порциями — таймаут не срабатывает,
а запрос может тянуться сколько угодно. Эта функция гарантирует реальный
верхний предел на весь запрос целиком через отдельный поток.

Используй вместо requests.get(...) в любом коллекторе:
    from app.http_utils import hard_timeout_get
    resp = hard_timeout_get(url, params=params, headers=headers, hard_timeout=35)
"""
import logging
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError

import requests

logger = logging.getLogger(__name__)


def hard_timeout_get(url: str, hard_timeout: float = 35, **kwargs) -> requests.Response:
    """Как requests.get, но с гарантированным верхним пределом времени.
    Бросает requests.Timeout, если не уложились — ловить так же, как обычный
    requests.exceptions.Timeout / RequestException."""

    def _do_request():
        return requests.get(url, **kwargs)

    pool = ThreadPoolExecutor(max_workers=1)
    try:
        future = pool.submit(_do_request)
        return future.result(timeout=hard_timeout)
    except FutureTimeoutError:
        raise requests.exceptions.Timeout(
            f"hard_timeout_get: {url} not completed within {hard_timeout}s"
        )
    finally:
        pool.shutdown(wait=False)
