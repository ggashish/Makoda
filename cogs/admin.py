import discord
import config
import importlib

from typing import Union
from discord.ext import commands
from utils import codeblock, make_error, paste, Context, is_owner


class Admin(commands.Cog):
    """Admin related commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(extras={"category": "general"})
    async def isadmin(self, ctx: Context, user: Union[discord.Member, discord.User]):
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
    async def reloadall(self, ctx: Context, name: str):
        """Reload all bot's extention."""

        error_collection = ""
        for extension in config.bot_extensions:
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


def setup(bot):
    bot.add_cog(Admin(bot))
