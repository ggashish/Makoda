import traceback
import discord
from discord.utils import escape_markdown
import mystbin

from typing import Union
from utils.paginator import pages, InteractionPages


def make_error(error):
    tb = traceback.format_exception(type(error), error, error.__traceback__)
    tbe = "".join(tb) + ""
    return tbe


async def safe_delete(message: discord.Message):
    try:
        await message.delete()
    except:
        pass


def codeblock(text):
    return f"```\n{text}```"


async def paste(text: str):
    mystbin_client = mystbin.Client()
    paste = await mystbin_client.post(text)
    return str(paste)


def num_suffix(num: int):
    def ordinal(n): return "%d%s" % (
        n, "tsnrhtdd"[(n//10 % 10 != 1)*(n % 10 < 4)*n % 10::4])
    return ordinal(num)


def get_url(my_object: Union[discord.User, discord.Member, discord.Guild]):
    if isinstance(my_object, (discord.User, discord.Member)):
        return my_object.avatar.url if my_object.avatar else discord.Embed.Empty

    if isinstance(my_object, discord.Guild):
        return my_object.icon.url if my_object.icon else discord.Embed.Empty


def discord_timestamp(time_to_convert, mode="R"):
    formated_strftime = f"<t:{int(time_to_convert.timestamp())}:{mode}>"

    return formated_strftime


def get_attachment(message: discord.Message):
    attachments_list = []
    if message.attachments:
        for count, attachments in enumerate(message.attachments, start=1):
            if attachments.size > 8388608:
                pass
            else:
                attachments_list.append(
                    f"[{num_suffix(count)} Attachment]({attachments.url})")

    if not attachments_list:
        return None

    else:
        return ", ".join(attachments_list)

async def message_data(message: discord.Message):
    show_msg = []
    if message.content:

        show_msg.append("Message: " + escape_markdown(message.content) if len(message.content) < 64 else f"Message: [Message too long click here to see the message]({await paste(message.content)})")

    if message.attachments:
        show_msg.append("Attachment(s): " + get_attachment(message))

    if message.embeds:
        show_msg.append(f"Embed(s): {len(message.embeds)}")

    return "\n".join(show_msg)


async def entries_paginator(ctx, entries, per_page=6, numbered=False, **kwargs):
    @pages(per_page=per_page)
    async def make_pages(self, menu: InteractionPages, entries) -> discord.Embed:
        embed = await kwargs_to_embed(ctx, **kwargs)
        embed.timestamp = discord.utils.utcnow()
        embed.description = "\n".join(map(str, entries)) if not numbered else '\n'.join(
            f'`[{i}]` {v}' for i, v in enumerate(entries, start=1))
        return embed

    menu = InteractionPages(make_pages(entries))
    await menu.start(ctx)


async def kwargs_to_embed(ctx, **kwargs):
    desc = kwargs.get('content', None)
    title = kwargs.get('title', None)
    url = kwargs.get('url', None)

    author = kwargs.get('author', None)
    colour = kwargs.get('colour', ctx.bot.colour)
    fields = kwargs.get('fields', None)
    image = kwargs.get('image', None)
    thumbnail = kwargs.get('thumbnail', None)
    timestamp = kwargs.get('timestamp', None)
    footer = kwargs.get('footer', None)

    embed = discord.Embed(colour=colour)

    embed.description = desc

    if title:
        embed.title = title

    if url:
        embed.url = url

    if timestamp:
        embed.timestamp = timestamp

    if image:
        embed.set_image(url=image)

    if thumbnail:
        embed.set_thumbnail(url=thumbnail)

    if author is not None:
        if isinstance(author, (discord.Member or discord.User)):
            icon_url = author.avatar.url
        elif isinstance(author, discord.Guild):
            icon_url = author.icon.url if author.icon else discord.Embed.Empty

        embed.set_author(name=author, icon_url=icon_url)

    if footer is not None:
        embed.set_author(name=footer, icon_url=footer.avatar.url if type(
            footer) == discord.Member else footer.icon.url)

    if fields is not None:
        for field in fields:
            if "index" not in field:
                embed.add_field(name=field["name"],
                                value=field["value"], inline=False)
            else:
                embed.insert_field_at(field["index"],
                                      name=field["name"], value=field["value"], inline=False)

    return embed
