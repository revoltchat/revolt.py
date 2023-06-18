import asyncio
import os
from dotenv import load_dotenv
import aiohttp
import revolt

load_dotenv()
token = os.getenv('TOKEN')

# Create a file in your bot's core directory called ".env".
# Add the following line to the .env file you just created:
# TOKEN=TOKEN_GOES_HERE

class Client(revolt.Client):
    async def on_message(self, message: revolt.Message):
        if message.content == "hello":
            await message.channel.send("hi how are you")

async def main():
    async with aiohttp.ClientSession() as session:
        client = Client(session, token)
        await client.start()

asyncio.run(main())
