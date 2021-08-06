import discord
import pytz
import re

from utils.exceptions import *
from discord.ext import commands


class URL(commands.Converter):
    async def convert(self, ctx, argument):
        url_regex = "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        if url_regex:
            return argument
        else:
            raise InvalidUrl(argument)