# eludris.py

## Usage

```python
import asyncio

import eludris

client = eludris.Client(
    "Botty"
)

@client.on_message
async def on_message(message):
    if message.author != client.name:
        await client.send(f"Hello {message.author}!")

asyncio.run(client.run())
```

## JWT
Because of Eludris' design, there is no way to confirm a message is from a you.

Thats why `eludris.py` can use JWT to verify the message is from you.

Install `pyjwt` and pass a `JWTConfig` to the `Client` constructor to enable this feature.

Your client also needs to append a JWT with `{"content": <content>, "author": <author>}` as the claim to the end of your message.

```python
Client(
    "Botty",
    jwt=JWTConfig(
        secret="secret",
        algorithm="HS256",
    )
)
```