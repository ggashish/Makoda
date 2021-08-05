import discord
import asyncio
import aiohttp
import config

from tortoise import Tortoise
from discord.ext import commands

from colorama import Fore, Style, init
from utils.helper import make_error
from discord.ext.commands import AutoShardedBot

init(autoreset=True)


class Bot(AutoShardedBot):
    def __init__(self, **kwargs):
        super().__init__(
            command_prefix=config.bot_prefix,
            strip_after_prefix=True,
            case_insensitive=True,
            reconnect=True,

            allowed_mentions=discord.AllowedMentions(
                everyone=False, roles=False, replied_user=False),
            intents=discord.Intents.all(),
            status=discord.Status.online,
            activity=discord.ActivityType.listening, name=config.bot_activity,
            **kwargs
        )

        asyncio.get_event_loop().run_until_complete(self.init_tourtoise())
        self.loop = asyncio.get_event_loop()
        self.colour = config.embed_colour
        self.version = config.version

        self.boot_time = discord.utils.utcnow()
        self.support_server = config.support_server
        self.invite_link = discord.utils.oauth_url(
            self.id, permissions=discord.Permissions.all())
        self.bot_owner_ids = config.bot_owners

        for extensions in config.extentions:
            try:
                self.load_extension(extensions)
                print(Fore.YELLOW +
                      f"[EXTENSION] {extensions} was loaded successfully!")
            except Exception as e:
                error = make_error(e)
                print(
                    Fore.RED + f"[WARNING] Could not load extension {extensions}: {error}")

        print()
        print(Fore.YELLOW + "------------------------------------------------------")

    @property
    def db(self):
        return Tortoise.get_connection("default")._pool

    async def init_tourtoise(self):
        self.session = aiohttp.ClientSession(loop=self.loop)
        await Tortoise.init(config.TORTOISE)
        await Tortoise.generate_schemas(safe=True)

        for mname, model in Tortoise.apps.get("models").items():
            model.bot = self

    async def on_ready(self):
        print(Fore.GREEN + "Logging in...")
        print(Fore.YELLOW + "------------------------------------------------------")
        print()
        print(Style.BRIGHT + f"Logged in as {self.user.name}({self.user.id})")
        print(Style.BRIGHT + f"Currently in {len(self.guilds)} Server")
        print(Style.BRIGHT + f"Connected to {len(self.users)} Users")

        self.load_extension("jishaku")

    def get_message(self, message_id: int) -> discord.Message:
        """Gets the message from the cache"""
        return self._connection._get_message(message_id)

    async def close(self):
        await super().close()
        await self.session.close()


if __name__ == "__main__":
    bot = Bot(description=config.bot_description)
    bot.run(config.bot_token)
