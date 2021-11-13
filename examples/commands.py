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
        client = Client(session, "BOT TOKEN HERE")
        await client.start()

asyncio.run(main())
