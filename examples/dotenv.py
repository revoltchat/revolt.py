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
    # The comment on line 24 exists to suppress a Pyright error on the GitHub repository
    # due to the '.env' file not existing and therefore the token not being accessible.
    # You can remove these comments if you're using this example as intended.
    async with aiohttp.ClientSession() as session:
        client = Client(session, token) # reportGeneralTypeIssues: ignore 
        await client.start()

asyncio.run(main())
