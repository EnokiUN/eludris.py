from asyncio import Queue
import asyncio
from typing import List, Optional, cast
import aiohttp

from .types import JWTConfig, Message, MessageListener


def jwt_support(message: Message, config: JWTConfig):
    import jwt

    try:
        claim = jwt.decode(
            message.content.split()[-1], config.secret, algorithms=[config.algorithm]
        )
        if (
            claim["content"] != " ".join(message.content.split()[:-1])
            or claim["author"] != message.author
        ):
            raise ValueError("Invalid claim")
        message.content = " ".join(message.content.split()[:-1])
    except Exception as e:
        return True


class Client:
    def __init__(self, name: str, jwt: Optional[JWTConfig] = None) -> None:
        self.name = name
        self.jwt = jwt
        self.session: aiohttp.ClientSession = cast(aiohttp.ClientSession, None)
        self.ws: aiohttp.ClientWebSocketResponse = cast(
            aiohttp.ClientWebSocketResponse, None
        )
        self.events = {"message": []}
        self.waiters: List[Queue] = []

    async def loop(self) -> None:
        async for data in self.ws:
            try:
                message = Message(data.json())
                print(message)
                if self.jwt and jwt_support(message, self.jwt):
                    continue

                for listener in self.events["message"]:
                    asyncio.create_task(listener(message))
                for waiter in self.waiters:
                    await waiter.put(message)

            except (ValueError, TypeError):
                continue

    async def send(self, message: str) -> None:
        await self.session.post(
            "https://eludris.tooty.xyz", json={"author": self.name, "content": message}
        )

    async def wait_for_message(self, author: str) -> Message:
        queue = Queue()
        self.waiters.append(queue)
        while True:
            message = await queue.get()
            if message.author == author:
                return message

    def on_message(self, callback: MessageListener):
        self.events["message"].append(callback)

    async def run(self) -> None:
        self.session = aiohttp.ClientSession()
        while True:
            self.ws = await self.session.ws_connect("wss://eludris.tooty.xyz/ws")
            await self.loop()
