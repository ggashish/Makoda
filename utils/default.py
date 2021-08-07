import discord
import pygit2
import itertools


class CustomButton(discord.ui.Button):
    def __init__(self, style: discord.ButtonStyle, label: str, custom_id: str = None, url: str = None):
        super().__init__()
        self.style = style
        self.label = label
        self.custom_id = custom_id
        self.url = url

    async def callback(self, interaction: discord.Interaction):
        self.view.stop()
        self.view.custom_id = self.custom_id
        self.view.label = self.label
        return self.custom_id


class CustomButtonView(discord.ui.View):
    def __init__(self, ctx, buttons, timeout=120, disable_button=True):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.author = ctx.author
        self.custom_id = None
        self.disable_button = disable_button

        for item in buttons:
            if item.custom_id:
                self.add_item(CustomButton(style=item.style,
                                           label=item.label, custom_id=item.custom_id))
            else:
                self.add_item(CustomButton(style=item.style,
                                           label=item.label, custom_id=item.custom_id, url=item.url))

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user != self.author:
            await interaction.response.send_message("Sorry, you can't use this interaction as it is not started by you.", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        self.custom_id = None
        bot = self.ctx.bot

        if self.disable_button:
            message = None
            for m_id, view in bot._connection._view_store._synced_message_views.items():
                if view is self:
                    if m := bot.get_message(m_id):
                        message = m

            if message is None:
                return

            for b in self.children:
                b.disabled = True
            await message.edit(view=self)

            await self.ctx.error("Time limit exceeded, please try again.")