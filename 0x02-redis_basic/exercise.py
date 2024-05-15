#!/usr/bin/env python3

"""Import modules"""

import functools
import redis
from uuid import uuid4
from typing import Union, Callable, Any, Optional


"""create a function"""


def call_history(method: Callable) -> Callable:
    """Decorator that maintains the history of method calls in history"""

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs) -> Any:
        """function that increments the count in Redis for the given method"""
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"

        normalized_input = str(args)
        self._redis.rpush(input_key, normalized_input)
        outputs = method(self, *args, **kwargs)
        self._redis.rpush(output_key, outputs)
        return outputs
    return wrapper


def replay(method: Callable) -> None:
    """Display the history of calls of a particular function."""
    redis_instance = method.__self__._redis

    inputs = redis_instance.lrange(f"{method.__qualname__}:inputs", 0, -1)
    outputs = redis_instance.lrange(f"{method.__qualname__}:outputs", 0, -1)

    print(f"{method.__qualname__} was called {len(inputs)} times:")

    for in_arg, out_arg in zip(inputs, outputs):
        print(f"{method.__qualname__}(*{in_arg.decode('utf-8')}) -> \
                {out_arg.decode('utf-8')}")


"""Create a Class"""


class Cache:
    """class for writing strings to Redis"""
    def __init__(self):
        """function for initiating strings"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """method that creates a store"""
        key = str(uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str,
            fn: Optional[Callable] = None) -> \
            Union[str, bytes, int, float, None]:
        """method that take a key string argument and Callable argument"""
        value = self._redis.get(key)
        if value is None:
            return None
        if fn:
            return fn(value)
        return value

    def get_str(self, key: str) -> Optional[str]:
        """Method that will automatically parametrize"""
        return self.get(key, fn=lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> Optional[int]:
        """method that with automatically parameterize int"""
        return self.get(key, fn=int)
