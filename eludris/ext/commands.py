from typing import List, Optional

from ..objects import JWTConfig, Message
from ..client import Client


class Context:
    def __init__(self, command: str, message: Message, bot: 'Bot') -> None:
        self.command: str = command
        self.author: str = message.author
        self.message: Message = message
        self.args: List[str] = message.content[message.content.find(command)+len(command):].split()
        self.bot: 'Bot' = bot

class Bot(Client):
    def __init__(self, name: str, prefix: str,  jwt: Optional[JWTConfig] = None) -> None:
        super().__init__(name, jwt)
        self.prefix = prefix
        self.commands: dict = {"help": self.help}
        self.on_message(self.process_commands)

    async def help(self, _: Context):
        groups = {
            "uncategorized": [],
        }
        for command in self.commands:
            if len(command.split()) > 1:
                groups[command.split()[0]] = groups.get(command.split()[0], []) + [command]
            else:
                groups["uncategorized"].append(command)
        for group in groups:
            await self.send(f"{group}: {', '.join(groups[group])}")


    def command(self, name: Optional[str] = None):
        def decorator(func):
            self.commands[name or func.__name__] = func
            return func
        return decorator

    async def process_commands(self, message: Message):
        if message.author == self.name:
            return
        if message.content.startswith(self.prefix):
            content = message.content[len(self.prefix):]
            for command in self.commands:
                if content.startswith(command):
                    ctx = Context(command, message, self)
                    await self.commands[command](ctx, *ctx.args)
                    break