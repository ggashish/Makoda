import discord

from model.functions import *
from tortoise import fields, models
from tortoise.models import Model

__all__ = ("Guild")


class Guild(Model):
    class Meta:
        table = "guild_data"

    guild_id = fields.BigIntField(pk=True, index=True)
    prefix = fields.CharField(default="!", max_length=5)

    @property
    def guild(self):
        return self.bot.get_guild(self.guild_id)
