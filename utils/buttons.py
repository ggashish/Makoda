import discord

from discord.ui import View, Button

class ConfirmView(View):
    def __init__(self, ctx, timeout=120, disable_button=True):
        super().__init__()
        self.value = None
        self.ctx = ctx
        self.author = ctx.author
        self.disable_button = disable_button

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user != self.author:
            await interaction.response.send_message("Sorry, you can't use this interaction as it is not started by you.", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        self.custom_id = None
        bot = self.ctx.bot

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

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = True
        self.stop()

    @discord.ui.button(label='Deny', style=discord.ButtonStyle.danger)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = False
        self.stop()

    @discord.ui.button(label='Abort', style=discord.ButtonStyle.primary)
    async def abort(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = None
        self.stop()

    