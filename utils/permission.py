import discord
import config


def is_owner(ctx):
    """Checks if the author is one of the bot owner."""
    return ctx.author.id in config.bot_owners
