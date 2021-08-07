import discord
import os
import platform
import psutil
import inspect


from utils import discord_timestamp, emote, CustomButtonView, get_last_commits, Context, linecount
from collections import Counter
from glob import glob
from prettytable import PrettyTable
from discord.ext import commands


class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["linecount", "lc"], extras={"category": "stats"})
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    async def codestats(self, ctx: Context):
        """Shows how many lines/files were made for the bot."""
        x = PrettyTable()
        ctr = Counter()

        x.field_names = ["Code", "Count"]

        for ctr["files"], f in enumerate(glob("./**/*.py", recursive=True)):
            with open(f, encoding="UTF-8") as fp:
                for ctr["lines"], line in enumerate(fp, ctr["lines"]):
                    line = line.lstrip()
                    ctr["imports"] += line.startswith("import") + \
                        line.startswith("from")
                    ctr["classes"] += line.startswith("class")
                    ctr["comments"] += "#" in line
                    ctr["functions"] += line.startswith("def")
                    ctr["coroutines"] += line.startswith("async def")
                    ctr["docstrings"] += line.startswith(
                        '"""') + line.startswith("'''")
        x.add_rows(
            [
                ["Files", ctr["files"]],
                ["Lines", ctr["lines"]],
                ["Imports", ctr["imports"]],
                ["Classes", ctr["classes"]],
                ["Comments", ctr["comments"]],
                ["Functions", ctr["functions"]],
                ["Coroutines", ctr["coroutines"]],
                ["Docstrings", ctr["docstrings"]]
            ]
        )

        embed = discord.Embed(colour=self.bot.colour)
        embed.set_author(name=ctx.me, icon_url=ctx.me.avatar.url)
        embed.description = f"```ml\n{x}```"
        return await ctx.reply(embed=embed)

    @commands.command(aliases=["stats"], extras={"category": "stats"})
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    async def botinfo(self, ctx: Context):
        """Shows info about the bot."""
        bot_uptime = discord_timestamp(self.bot.boot_time)
        created = discord_timestamp(self.bot.user.created_at)
        bot_guilds = len(self.bot.guilds)
        bot_users = len(self.bot.users)

        dpy_version = f"[Discord.py v{discord.__version__}](https://github.com/Rapptz/discord.py)"
        py_version = f"[Python v{platform.python_version()}](https://www.python.org/)"
        bot_version = f"[Makoda v{self.bot.version}]({self.bot.invite_link})"

        channel_types = Counter(type(c) for c in self.bot.get_all_channels())
        channels = channel_types[discord.channel.TextChannel]
        voice_channel = channel_types[discord.channel.VoiceChannel]

        ashish = self.bot.get_user(711043296025378856)
        latency = f"{round(ctx.bot.latency*1000, 2)} ms"

        pid = os.getpid()
        py = psutil.Process(pid)
        memory_use = py.memory_info()

        cpu = f"{psutil.cpu_percent()}%"
        total_ram_usage = f"{round(psutil.virtual_memory().used/1024/1024)}MB"
        py_ram_usage = f"{round(memory_use[0] / 1024 / 1024)}MB"

        recent_updates = get_last_commits()

        embed = discord.Embed(colour=self.bot.colour)
        embed.set_author(
            name=f"About {self.bot.user}", icon_url=self.bot.user.avatar.url)
        embed.description = f"{ctx.guild.me.mention} is simple discord bot that helps you getting started within discord.py with asyncpg & tortoise-orm."

        embed.add_field(
            name="**__Makoda Info__**", value=f"**Created:** {created}\n**Online Since:** {bot_uptime}\n**Latency:** {latency}", inline=False)
        embed.add_field(
            name="**__System Info__**", value=f"**CPU Usage:** {cpu}\n**RAM Usage:** `{total_ram_usage}` (`{py_ram_usage}` is unique to this process)", inline=False)
        embed.add_field(
            name="**__Total__**", value=f"**Bot Server(s):** {bot_guilds}\n**Bot User(s):** {bot_users}\n**Bot Channel(s):** {emote.channel} {channels} | {emote.voice} {voice_channel}\n**Code Line(s)**: {linecount()}", inline=False)
        embed.add_field(
            name="**__Version Info__**", value=f"{emote.python} {py_version}\n{emote.discord} {dpy_version}\n{emote.bot} {bot_version}", inline=False)
            
        embed.add_field(name="**__Latest Changes__**", value=recent_updates, inline=False)
        buttons = [
            discord.ui.Button(style=discord.ButtonStyle.link, label="Invite Makoda", url=self.bot.invite_link),
            discord.ui.Button(style=discord.ButtonStyle.link, label="Source Code", url=self.bot.source_code),
            discord.ui.Button(style=discord.ButtonStyle.link, label="Support Server", url=self.bot.support_server),
            discord.ui.Button(style=discord.ButtonStyle.link, label="Makoda Developer", url=f"https://discord.com/users/{ashish.id}")
        ]
        view = CustomButtonView(ctx, buttons, disable_button=False)
        return await ctx.reply(embed=embed, view=view)

    @commands.command(extras={"category": "stats"})
    async def source(self, ctx: Context, *, search: str = None):
        """Refer to the source code of the bot commands."""
        source_url = "https://github.com/ggashish/Makoda"

        if search is None:
            return await ctx.send(f"<{source_url}>")

        command = self.bot.get_command(search)

        if not command:
            return await ctx.failure("Couldn't find that command.")

        src = command.callback.__code__
        filename = src.co_filename
        lines, firstlineno = inspect.getsourcelines(src)

        location = os.path.relpath(filename).replace("\\", "/")

        final_url = f"<{source_url}/blob/main/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1}>"
        await ctx.send(final_url)

def setup(bot):
    bot.add_cog(Information(bot))
