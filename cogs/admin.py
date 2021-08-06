import discord
from discord.invite import I
from discord.utils import escape_markdown
import config
import importlib

from typing import Union
from discord.ext import commands
from utils import *


class Admin(commands.Cog):
    """Admin related commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(extras={"category": "general"})
    async def isadmin(self, ctx: Context, user: Union[discord.Member, discord.User]=None):
        """Checks and tell if the user is one of the bot admin."""
        user = user or ctx.author

        if user.id in config.bot_owners:
            return await ctx.success(f"Yes! {user} is an bot's admin.")

        return await ctx.failure(f"No! {user} is not an bot's admin.")

    @commands.command(extras={"category": "extentions"})
    @commands.check(is_owner)
    async def load(self, ctx: Context, name: str):
        """Load an bot's extention."""
        try:
            self.bot.load_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.failure(f"There was an error loading ***{name}.py***\n" + codeblock(make_error(e)))

        await ctx.success(f"Successfully loaded ***{name}.py***")

    @commands.command(extras={"category": "extentions"})
    @commands.check(is_owner)
    async def unload(self, ctx: Context, name: str):
        """Un-Load an bot's extention."""
        try:
            self.bot.unload_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.failure(f"There was an error unloading ***{name}.py***\n" + codeblock(make_error(e)))

        await ctx.success(f"Successfully un-loaded ***{name}.py***")

    @commands.command(extras={"category": "extentions"})
    @commands.check(is_owner)
    async def reload(self, ctx: Context, name: str):
        """Reload an bot's extention."""
        try:
            self.bot.reload_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.failure(f"There was an error reloading ***{name}.py***\n" + codeblock(make_error(e)))

        await ctx.success(f"Successfully reloded ***{name}.py***")

    @commands.command(extras={"category": "extentions"})
    @commands.check(is_owner)
    async def reloadall(self, ctx: Context):
        """Reload all bot's extention."""

        error_collection = ""
        for extension in config.extentions:
            try:
                self.bot.reload_extension(extension)
                error_collection += f"\n🔁 Reloaded `{extension}`"
            except Exception as e:
                error_collection += f"\n❌ Unable to reload `{extension}` ([Error]({await paste(e)}))"
                error_collection.append((make_error(e)))

        embed = discord.Embed(
            title="All Extentions reloaded", colour=self.bot.colour)
        embed.description = error_collection
        embed.timestamp = discord.utils.utcnow()

        await ctx.reply(embed=embed)

    @commands.command(extras={"category": "extentions"})
    @commands.check(is_owner)
    async def reloadutil(self, ctx: Context, name: str):
        """Reload an util module."""

        try:
            module_name = importlib.import_module(f"utils.{name}")
            importlib.reload(module_name)
        except ModuleNotFoundError:
            return await ctx.failure(f"Couldn't find module named ***utils/{name}***")

        except Exception as e:
            return await ctx.failure(f"There was an error reloading ***utils/{name}***\n" + codeblock(make_error(e)))

        await ctx.success(f"Successfully reloded ***{name}.py*** util module.")

    @commands.group(invoke_without_command=True, extras={"category": "dm"})
    @commands.check(is_owner)
    async def dm(self, ctx: Context, user: Union[discord.User, discord.Member], *, message: str):
        """Lets the bot dm the user of your choice."""
        try:
            embed = discord.Embed(colour=self.bot.colour)
            embed.set_author(name=ctx.author, icon_url=get_url(ctx.author))
            embed.timestamp = discord.utils.utcnow()
            embed.description = message
            await user.send(embed=embed)

            return await ctx.success(f"Successfully sent DM to `{escape_markdown(str(user))}`")

        except discord.Forbidden:
            return await ctx.failure(f"I was unable to send DM to `{escape_markdown(str(user))}`, either the user's DM are closed of the user have blocked me.")

    @dm.command(name="all", extras={"category": "dm"})
    @commands.check(is_owner)
    async def dm_all(self, ctx: Context, user: Union[discord.User, discord.Member]):
        """Shows all latest 50 DM messages sent by the user in the bot's DM"""

        user_dms = await user.history(limit=50).flatten()
        if not user_dms:
            return await ctx.failure("User does not have any DMs with me. :(")

        entries = []
        for message in user_dms:
            content = await message_data(message)
            entries.append(
                f"***__{escape_markdown(message.author.name)} (ID: {message.id}) {discord_timestamp(message.created_at)}__***\n> {content}\n")

        await entries_paginator(ctx, entries, title=f"{escape_markdown(str(user))} DMs", thumbnail=get_url(user), url=f"https://discord.com/users/{user.id}")

    @dm.command(name="edit", extras={"category": "dm"})
    @commands.check(is_owner)
    async def dm_edit(self, ctx: Context, user: Union[discord.User, discord.Member], message_id: int, *, message: str):
        """Edits a message sent in user's dm"""

        get_message = await user.fetch_message(message_id)
        if not get_message:
            return await ctx.failure("Oops! I couldn't find message with that ID.")

        if not get_message.author.id == self.bot.user.id:
            return await ctx.failure("I can't edit other user messages :(")

        embed = discord.Embed(colour=self.bot.colour)
        embed.set_author(name=ctx.author, icon_url=get_url(ctx.author))
        embed.set_footer(text="Edited")
        embed.timestamp = discord.utils.utcnow()
        embed.description = message

        await get_message.edit(embed=embed)

        return await ctx.success(f"Successfully edited message with `ID {message_id}`")

    @dm.command(name="delete", extras={"category": "dm"})
    @commands.check(is_owner)
    async def dm_delete(self, ctx: Context, user: Union[discord.User, discord.Member], message_id: int):
        """Delete a message sent in user's dm"""

        get_message = await user.fetch_message(message_id)
        if not get_message:
            return await ctx.failure("Oops! I couldn't find message with that ID.")

        await get_message.delete()

        return await ctx.success(f"Successfully deleted message with `ID {message_id}`")

    @commands.group(invoke_without_command=True, extras={"category": "bot"})
    @commands.check(is_owner)
    async def change(self, ctx: Context):
        """Update bot information/data."""

        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @change.command(name="activity", extras={"category": "bot"})
    @commands.check(is_owner)
    async def change_activity(self, ctx: Context, name: str):
        """Change bot's activity."""

        if len(name) > 64:
            return await ctx.failure("I'm sorry but the maximum character limit is 64.")

        view = ActivityView(ctx, name)
        msg = await ctx.send("Choose an activity type from the button below.", view=view)
        await view.wait()

        if not view:
            await safe_delete(msg)
            return await ctx.success("Alright not updating bot's activity.")

        return await ctx.success("Successfully updated bot's activity.")

    @change.command(name="status", extras={"category": "bot"})
    @commands.check(is_owner)
    async def change_status(self, ctx: Context):
        """Change bot's status."""

        view = StatusView(ctx)
        msg = await ctx.send("Choose an status type from the button below.", view=view)
        await view.wait()

        if not view:
            await safe_delete(msg)
            return await ctx.success("Alright not updating bot's status.")

        return await ctx.success("Successfully updated bot's status.")

    @change.command(name="username", extras={"category": "bot"})
    @commands.check(is_owner)
    async def change_username(self, ctx: Context, name: str):
        """Change the bot's username"""

        if len(name) > 32:
            return await ctx.failure("I'm sorry but the maximum character limit is 32.")

        await self.bot.user.edit(username=name)
        return await ctx.success(f"Successfully updated username to `{escape_markdown(name)}`")

    @change.command(name="nickname", aliases=["nick"], extras={"category": "bot"})
    @commands.check(is_owner)
    async def change_username(self, ctx: Context, name: str=None):
        """Change the bot's nickname for the server."""

        if len(name) > 32:
            return await ctx.failure("I'm sorry but the maximum character limit is 32.")

        await ctx.guild.me.edit(nick=name)
        return await ctx.success(f"Successfully updated nickname to {escape_markdown(name) if name else 'default'}.")

    @change.command(name="avatar", extras={"category": "bot"})
    @commands.check(is_owner)
    async def change_avatar(self, ctx, url: URL):
        """Change bot's avatar."""
        pass




def setup(bot):
    bot.add_cog(Admin(bot))
