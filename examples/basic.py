import asyncio
import aiohttp
import revolt


class Client(revolt.Client):
    async def on_message(self, message: revolt.Message):
        if message.content == "hello":
            await message.channel.send("hi how are you")

async def main():
    async with aiohttp.ClientSession() as session:
        # Storing the token in source code like this is bad practice. Please see the "dotenv" example for a more secure way of storing bot tokens.
        client = Client(session, "BOT TOKEN HERE")
        await client.start()

asyncio.run(main())
