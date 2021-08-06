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

        await self.ctx.failure("Time limit exceeded, please try again.")

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


class ActivityView(View):
    def __init__(self, ctx, name: str, timeout=60):
        super().__init__()
        self.value = None
        self.ctx = ctx
        self.bot = ctx.bot
        self.author = ctx.author
        self.name = name
        self.activity = None

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

        await self.ctx.failure("Time limit exceeded, please try again.")

    @discord.ui.button(label='Playing', style=discord.ButtonStyle.primary)
    async def playing(self, button: discord.ui.Button, interaction: discord.Interaction):
        game = discord.Activity(type=0, name=self.name)
        await self.bot.change_presence(activity=game)
        self.activity = "playing"
        self.stop()

    @discord.ui.button(label='Listening', style=discord.ButtonStyle.primary)
    async def listening(self, button: discord.ui.Button, interaction: discord.Interaction):
        game = discord.Activity(type=2, name=self.name)
        await self.bot.change_presence(activity=game)
        self.activity = "listening"
        self.stop()

    @discord.ui.button(label='Watching', style=discord.ButtonStyle.primary)
    async def watching(self, button: discord.ui.Button, interaction: discord.Interaction):
        game = discord.Activity(type=3, name=self.name)
        await self.bot.change_presence(activity=game)
        self.activity = "watching"
        self.stop()

    @discord.ui.button(label='Competing', style=discord.ButtonStyle.primary)
    async def competing(self, button: discord.ui.Button, interaction: discord.Interaction):
        game = discord.Activity(type=5, name=self.name)
        await self.bot.change_presence(activity=game)
        self.activity = "competing"
        self.stop()

    @discord.ui.button(label='Abort', style=discord.ButtonStyle.danger)
    async def abort(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.stop()
        self.activity = False

class StatusView(View):
    def __init__(self, ctx, timeout=60):
        super().__init__()
        self.value = None
        self.ctx = ctx
        self.bot = ctx.bot
        self.author = ctx.author

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

        await self.ctx.failure("Time limit exceeded, please try again.")

    @discord.ui.button(label='Offline', style=discord.ButtonStyle.primary)
    async def offline(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.bot.change_presence(status=discord.Status.offline)
        self.stop()

    @discord.ui.button(label='Online', style=discord.ButtonStyle.primary)
    async def online(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.bot.change_presence(status=discord.Status.online)
        self.stop()

    @discord.ui.button(label='Idle', style=discord.ButtonStyle.primary)
    async def idle(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.bot.change_presence(status=discord.Status.idle)
        self.stop()

    @discord.ui.button(label='DND', style=discord.ButtonStyle.primary)
    async def dnd(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.bot.change_presence(status=discord.Status.dnd)
        self.stop()
        
    @discord.ui.button(label='Abort', style=discord.ButtonStyle.danger)
    async def abort(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.stop()
        self.value = None