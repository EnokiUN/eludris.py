from collections import namedtuple
from typing import Any, Callable, Coroutine, TypedDict

JWTConfig = namedtuple("JWTConfig", ["secret", "algorithm"])

class MessagePayload(TypedDict):
    author: str
    content: str


class Message:
    def __init__(self, message: MessagePayload) -> None:
        self.author = message["author"]
        self.content = message["content"]

    def __repr__(self) -> str:
        return f"<Message author={self.author!r} content={self.content!r}>"


MessageListener = Callable[[Message], Coroutine[Any, Any, Any]]
