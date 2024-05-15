#!/usr/bin/env python3
"""Implementing an expiring web cache and tracker"""
import redis
import requests
from functools import wraps
from typing import Callable

redis_store = redis.Redis()
'''The module-level Redis instance.
'''

def cache_result(ttl: int = 10) -> Callable:
    """Cache the result of a function call with an expiration time"""
    def wrapper(method: Callable) -> Callable:
        @wraps(method)
        def wrapped(url: str) -> str:
            """wrapped"""
            redis_store.incr(f'count:{url}')
            result = redis_store.get(f'result:{url}')
            if result is not None:
                return result.decode('utf-8')
            try:
                result = method(url)
                if result is not None:
                    redis_store.setex(f'result:{url}', ttl, result)
                return result
            except requests.RequestException as e:
                print(f"Error fetching {url}: {e}")
                return None
        return wrapped
    return wrapper

@cache_result(ttl=10)
def get_page(url: str) -> str:
    """get_page"""
    res = requests.get(url)
    return res.text
