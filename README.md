# Revolt.py

An async library to interact with the [Revolt API](https://revolt.chat). This library will **only support bots** and I will **not** implement anything exclusively for user accounts.

You can join the support server [here](https://rvlt.gg/FDXER6hr) and find the library's documentation [here](https://revoltpy.readthedocs.io/en/latest/). 

## Installing

You can use `pip` to install `revolt.py`. It differs slightly depending on what OS/Distro you are using.

On Windows
```
py -m pip install -U revolt.py # -U to update
```

On macOS and Linux
```
python3 -m pip install -U revolt.py
```

## Example

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

More examples can be found in the [examples folder](https://github.com/revoltchat/revolt.py/blob/master/examples).
