import discord

from discord.utils import escape_mentions
from discord.ext import commands
from discord.ext.commands import Cog


class Error(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_command_error(self, ctx, error):

        if hasattr(ctx.command, "on_error"):
            return

        if isinstance(error, commands.CommandNotFound):
            return

        elif isinstance(error, commands.CheckFailure):
            return await ctx.embed_error(escape_mentions(str(error)))

        elif isinstance(error, commands.NSFWChannelRequired):
            return await ctx.error("This command requires a NSFW channel.")

        elif isinstance(error, commands.BadArgument):
            return await ctx.error(escape_mentions(str(error)))

        elif isinstance(error, commands.MissingRequiredArgument):
            if not isinstance(ctx.command, commands.Group):
                return await ctx.error(f"{ctx.author.mention}, You missed a required argument `{error.param.name}`\n\nHow to use the command: `{ctx.command.signature}`")
            else:
                return await ctx.send_help(ctx.command)

        elif isinstance(error, commands.TooManyArguments):
            if isinstance(ctx.command, commands.Group):
                return

        elif isinstance(error, commands.NotOwner):
            return await ctx.error("I didn't knew you are the owner. 🤔")

        elif isinstance(error, commands.MissingPermissions):
            perms = "`" + "`, `".join(error.missing_perms) + "`"
            return await ctx.error(f"You're missing {perms} permissions.")

        elif isinstance(error, commands.BotMissingPermissions):
            perms = "`" + "`, `".join(error.missing_perms) + "`"
            return await ctx.error(f"I'm missing {perms} permissions.")

        elif isinstance(error, commands.MaxConcurrencyReached):
            return await ctx.error(f"This command is already running in this server. You have wait for it to finish.")

        elif isinstance(error, commands.CommandOnCooldown):
            is_owner = await ctx.bot.is_owner(ctx.author)
            if is_owner is True:
                return await ctx.reinvoke()
            await ctx.send(f"You are in cooldown.\n\nTry again in `{error.retry_after:.2f}` seconds.")
            return

        elif isinstance(error, commands.PrivateMessageOnly):
            return await ctx.error("This command can only be used in private message.")

        elif isinstance(error, commands.NoPrivateMessage):
            return await ctx.error("This command can't be used in private message.")

        elif isinstance(error, commands.ExpectedClosingQuoteError):
            return await ctx.error("You failed to close the quote.")

        else:
            print(error)

def setup(bot):
    bot.add_cog(Error(bot))