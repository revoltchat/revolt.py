# Revolt.py

[![PyPI version info](https://img.shields.io/pypi/v/revolt.py.svg)](https://pypi.python.org/pypi/revolt.py)
[![PyPI supported Python versions](https://img.shields.io/pypi/pyversions/revolt.py.svg)](https://pypi.python.org/pypi/revolt.py)

An async library to interact with the [Revolt](https://revolt.chat) API.

## Key Features
- Modern Pythonic API using ``async`` and ``await``.
- Proper rate limit handling.
- Optimised in both speed and memory.

## Installing

**Python 3.9 or higher is required**

You can use `pip` to install `revolt.py`. It differs slightly depending on what OS/Distro you are using.

```shell
# Windows
py -m pip install -U revolt.py # -U to update

# macOS/Linux
python3 -m pip install -U revolt.py
```

## Example

```python
import revolt
import asyncio
import aiohttp

class Client(revolt.Client):
    async def on_message(self, message: revolt.Message):
        if message.content.lower() == "hello":
            await message.channel.send("Hello! How are you?")

async def main():
    async with aiohttp.ClientSession() as session:
        client = Client(session, "BOT TOKEN HERE")
        await client.start()

asyncio.run(main())
```

More examples can be found in the [examples folder](https://github.com/revoltchat/revolt.py/blob/master/examples).

## Links

- [Documentation](https://revoltpy.readthedocs.io/en/latest/)
- [Official Revolt Server](https://rvlt.gg/FDXER6hr/)
- [Revolt API](https://developers.revolt.chat/)
