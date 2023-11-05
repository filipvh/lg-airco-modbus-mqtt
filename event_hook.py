from collections.abc import Callable
from typing import Generic, TypeVar

T = TypeVar('T')


class EventHook(Generic[T]):
    def __init__(self):
        self.__handlers: Callable[[T]] = []

    def add_handler(self, handler: Callable[[T], None]):
        self.__handlers.append(handler)

    def fire(self, event_args: T):
        for handler in self.__handlers:
            handler(event_args)

    def clear(self):
        self.__handlers = []
