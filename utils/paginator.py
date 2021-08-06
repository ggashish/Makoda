import discord
import datetime
import re

from copy import copy
from discord import ui
from functools import partial
from discord.ext import menus
from discord.ext import commands
from discord.ui import View, Button
from discord.ext.menus import First, Last, PageSource
from typing import Optional, Any, Dict, Iterable, Union, Type, Coroutine, Callable, Tuple, List

PAGE_REGEX = r'(Page)?(\s)?((\[)?((?P<current>\d+)/(?P<last>\d+))(\])?)'


class MenuBase(menus.MenuPages):
    """This is a MenuPages class that is used every single paginator menus. All it does is replace the default emoji
       with a custom emoji, and keep the functionality."""

    def __init__(self, source: PageSource, *, generate_page: bool = True, **kwargs: Any):
        super().__init__(source, delete_message_after=kwargs.pop(
            'delete_message_after', True), **kwargs)
        self.info = False
        self._generate_page = generate_page

    @menus.button("◀️", position=First(1))
    async def go_before(self, _: discord.RawReactionActionEvent):
        """Goes to the previous page."""
        await self.show_checked_page(self.current_page - 1)

    @menus.button("▶️", position=Last(0))
    async def go_after(self, _: discord.RawReactionActionEvent):
        """Goes to the next page."""
        await self.show_checked_page(self.current_page + 1)

    @menus.button("⏮️", position=First(0))
    async def go_first(self, _: discord.RawReactionActionEvent):
        """Goes to the first page."""
        await self.show_page(0)

    @menus.button("⏭️", position=Last(1))
    async def go_last(self, _: discord.RawReactionActionEvent):
        """Goes to the last page."""
        await self.show_page(self._source.get_max_pages() - 1)

    @menus.button("⏹️", position=First(2))
    async def go_stop(self, _: discord.RawReactionActionEvent):
        """Remove this message."""
        self.stop()

    async def _get_kwargs_format_page(self, page: Any) -> Dict[str, Any]:
        value = await discord.utils.maybe_coroutine(self._source.format_page, self, page)
        if self._generate_page:
            value = self.generate_page(value, self._source.get_max_pages())
        if isinstance(value, dict):
            return value
        elif isinstance(value, str):
            return {'content': value, 'embed': None}
        elif isinstance(value, discord.Embed):
            return {'embed': value, 'content': None}

    async def _get_kwargs_from_page(self, page: Any) -> Dict[str, Any]:
        dicts = await self._get_kwargs_format_page(page)
        dicts.update(
            {'allowed_mentions': discord.AllowedMentions(replied_user=False)})
        return dicts

    def generate_page(self, content: Union[discord.Embed, str], maximum: int) -> Union[discord.Embed, str]:
        if maximum > 0:
            page = f"Page {self.current_page + 1}/{maximum}"
            if isinstance(content, discord.Embed):
                if embed_dict := getattr(content, "_author", None):
                    if not re.match(PAGE_REGEX, embed_dict["name"]):
                        embed_dict["name"] += f"[{page.replace('Page ', '')}]"
                    return content
                return content.set_author(name=page)
            elif isinstance(content, str) and not re.match(PAGE_REGEX, content):
                return f"{page}\n{content}"
        return content

    async def send_initial_message(self, ctx: commands.Context, channel: discord.TextChannel) -> discord.Message:
        page = await self._source.get_page(0)
        kwargs = await self._get_kwargs_from_page(page)
        return await ctx.reply(**kwargs)


def pages(per_page: Optional[int] = 1, show_page: Optional[bool] = True) -> Callable:
    """Compact ListPageSource that was originally made teru but was modified"""
    def page_source(coro: Callable[[MenuBase, Any], Coroutine[Any, Any, discord.Embed]]) -> Type[menus.ListPageSource]:
        async def create_page_header(self, menu: MenuBase, entry: Any) -> Union[discord.Embed, str]:
            result = await discord.utils.maybe_coroutine(coro, self, menu, entry)
            return menu.generate_page(result, self._max_pages)

        def __init__(self, list_pages: Iterable):
            super(self.__class__, self).__init__(list_pages, per_page=per_page)
        kwargs = {
            '__init__': __init__,
            'format_page': (coro, create_page_header)[show_page]
        }
        return type(coro.__name__, (menus.ListPageSource,), kwargs)
    return page_source


@pages()
def empty_page_format(_, __, entry: Any) -> Any:
    """This is for Code Block ListPageSource and for help Cog ListPageSource"""
    return entry


class BaseEmbed(discord.Embed):
    """Main purpose is to get the usual setup of Embed for a command or an error embed"""

    def __init__(self, color: Union[discord.Color, int] = 0xffcccb, timestamp: datetime.datetime = None,
                 fields: Tuple[Tuple[str, bool]] = (), field_inline: bool = False, **kwargs):
        super().__init__(color=color, timestamp=timestamp or datetime.datetime.utcnow(), **kwargs)
        for n, v in fields:
            self.add_field(name=n, value=v, inline=field_inline)

    @classmethod
    def default(cls, ctx: commands.Context, **kwargs) -> "BaseEmbed":
        instance = cls(**kwargs)
        instance.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
        return instance

    @classmethod
    def to_error(cls, title: str = "Error",
                 color: Union[discord.Color, int] = discord.Color.red(), **kwargs) -> "BaseEmbed":
        return cls(title=title, color=color, **kwargs)


class BaseButton(ui.Button):
    def __init__(self, *, style: discord.ButtonStyle, selected: Union[int, str], row: int,
                 label: Optional[str] = None, **kwargs: Any):
        super().__init__(style=style, label=label or selected, row=row, **kwargs)
        self.selected = selected

    async def callback(self, interaction: discord.Interaction) -> None:
        raise NotImplementedError


class ListPageInteractionBase(menus.ListPageSource):
    """A ListPageSource base that is involved with Interaction. It takes button and interaction object
        to correctly operate and require format_view to be overriden"""

    def __init__(self, button: Button, entries: Iterable[Any], **kwargs: Any):
        super().__init__(entries, **kwargs)
        self.button = button

    async def format_view(self, menu: menus.MenuPages, entry: Any) -> None:
        """Method that handles views, it must return a View"""
        raise NotImplementedError


class InteractionPages(ui.View, MenuBase):
    def __init__(self, source: ListPageInteractionBase, generate_page: Optional[bool] = False):
        super().__init__(timeout=300)
        self._source = source
        self._generate_page = generate_page
        self.ctx = None
        self.message = None
        self.current_page = 0
        self.current_button = None
        self.current_interaction = None
        self.cooldown = commands.CooldownMapping.from_cooldown(
            1, 10, commands.BucketType.user)

    async def start(self, ctx, /) -> None:
        self.ctx = ctx
        self.message = await self.send_initial_message(ctx, ctx.channel)

    def add_item(self, item: discord.ui.Item) -> None:
        coro = copy(item.callback)
        item.callback = partial(self.handle_callback, coro)
        super().add_item(item)

    async def handle_callback(self, coro: Callable[[discord.ui.Button, discord.Interaction], Coroutine[None, None, None]],
                              button: discord.ui.Button, interaction: discord.Interaction, /) -> None:
        self.current_button = button
        self.current_interaction = interaction
        await coro(button, interaction)

    @ui.button(emoji='⏮️')
    async def first_page(self, *_: Union[discord.ui.Button, discord.Interaction]):
        await self.show_page(0)

    @ui.button(emoji='◀️')
    async def before_page(self, *_: Union[discord.ui.Button, discord.Interaction]):
        await self.show_checked_page(self.current_page - 1)

    @ui.button(emoji='⏹️')
    async def stop_page(self, *_: Union[discord.ui.Button, discord.Interaction]):
        self.stop()
        await self.message.delete()

    @ui.button(emoji='▶️')
    async def next_page(self, *_: Union[discord.ui.Button, discord.Interaction]):
        await self.show_checked_page(self.current_page + 1)

    @ui.button(emoji='⏭️')
    async def last_page(self, *_: Union[discord.ui.Button, discord.Interaction]):
        await self.show_page(self._source.get_max_pages() - 1)

    async def _get_kwargs_from_page(self, page: Any) -> Dict[str, Any]:
        value = await super()._get_kwargs_from_page(page)
        self.format_view()
        if 'view' not in value:
            value.update({'view': self})
        value.update(
            {'allowed_mentions': discord.AllowedMentions(replied_user=False)})
        return value

    def format_view(self) -> None:
        for i, b in enumerate(self.children):
            b.disabled = any(
                [self.current_page == 0 and i < 2, self.current_page ==
                    self._source.get_max_pages() - 1 and not i < 3]
            )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Only allowing the context author to interact with the view"""
        ctx = self.ctx
        author = ctx.author
        if interaction.user != author:
            bucket = self.cooldown.get_bucket(ctx.message)
            if not bucket.update_rate_limit():
                h = ctx.bot.help_command
                command = h.get_command_signature(ctx.command, ctx)
                content = f"Only `{author}` can use this menu. If you want to use it, use `{command}`"
                embed = BaseEmbed.to_error(description=content)
                await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        return True

    async def on_timeout(self) -> None:
        await self.message.delete()
