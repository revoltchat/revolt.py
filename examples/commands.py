import asyncio

import aiohttp

import revolt
from revolt.ext import commands


class Client(commands.CommandsClient):
    async def get_prefix(self, message: revolt.Message):
        return "!"

    @commands.command()
    async def ping(self, ctx: commands.Context):
        await ctx.send("pong")

async def main():
    async with aiohttp.ClientSession() as session:
        # Storing the token in source code like this is bad practice.
        # Please see the "dotenv" example for a more secure way of storing bot tokens.
        client = Client(session, "BOT TOKEN HERE")
        await client.start()

asyncio.run(main())
