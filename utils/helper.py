import traceback
import discord
import mystbin

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
