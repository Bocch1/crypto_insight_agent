"""
重试机制模块
使用 tenacity 实现指数退避重试
"""
from functools import wraps
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_log,
    after_log
)
from loguru import logger


def retry_with_backoff(
    max_attempts: int = 3,
    min_wait: int = 1,
    max_wait: int = 10
):
    """
    带指数退避的重试装饰器
    
    Args:
        max_attempts: 最大重试次数
        min_wait: 最小等待时间（秒）
        max_wait: 最大等待时间（秒）
    
    Example:
        @retry_with_backoff(max_attempts=3)
        def call_api():
            ...
    """
    def decorator(func):
        @wraps(func)
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
            retry=retry_if_exception_type((ConnectionError, TimeoutError, Exception)),
            before=before_log(logger, "DEBUG"),  # 修复：使用字符串 "DEBUG" 而不是 logger.level("DEBUG")
            after=after_log(logger, "DEBUG")     # 修复：使用字符串 "DEBUG" 而不是 logger.level("DEBUG")
        )
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator