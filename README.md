# Revolt.py

An async library to interact with the https://revolt.chat api.

This library will be focused on making bots and i will not implement anything only for user accounts.

Support server: https://app.revolt.chat/invite/FDXER6hr

Documentation is [here](https://revoltpy.readthedocs.io/en/latest/)

## Example

More examples in the [examples folder](https://github.com/zomatree/revolt.py/blob/master/examples)

```py
import revolt
import asyncio
import aiohttp

class Client(revolt.Client):
    async def on_message(self, message: revolt.Message):
        if message.content == "hello":
            await message.channel.send("hi how are you")

async def main():
    async with aiohttp.ClientSession() as session:
        client = Client(session, "BOT TOKEN HERE")
        await client.start()

asyncio.run(main())
```
