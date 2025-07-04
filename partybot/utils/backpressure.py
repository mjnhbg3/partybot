
import asyncio
from collections import deque
from typing import TypeVar, Generic

T = TypeVar("T")


class BackpressureQueue(Generic[T]):
    """A queue with a maximum size that drops the oldest items when full."""

    def __init__(self, maxsize: int):
        self._queue = deque(maxlen=maxsize)
        self._maxsize = maxsize
        self._event = asyncio.Event()

    async def put(self, item: T):
        """Puts an item into the queue."""
        self._queue.append(item)
        self._event.set()

    async def get(self) -> T:
        """Gets an item from the queue."""
        while not self._queue:
            await self._event.wait()
            self._event.clear()
        return self._queue.popleft()

    def qsize(self) -> int:
        """Returns the number of items in the queue."""
        return len(self._queue)

    def clear(self):
        """Clears the queue."""
        self._queue.clear()
