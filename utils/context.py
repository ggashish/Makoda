import discord

from utils import emote
from discord.ext import commands
from utils.helper import kwargs_to_embed, safe_delete
from utils.buttons import ConfirmView


class Context(commands.Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def success(self, message, delete_after=None):
        return await self.reply(f"{emote.confirm} | {message}", delete_after=delete_after)

    async def failure(self, message, delete_after=None):
        return await self.reply(f"{emote.deny} | {message}", delete_after=delete_after)

    async def confirm(self, **kwargs):
        view = ConfirmView(self, disable_button=False)
        embed = await kwargs_to_embed(self, **kwargs)
        message = await self.send(embed=embed, view=view)
        await view.wait()

        if view.value:
            confirm = True

        if view.value is False:
            confirm = False

        if view.value is None:
            await safe_delete(message)
            return None

        await safe_delete(message)
        return confirm
