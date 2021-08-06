from discord.ext import commands


class CustomError(commands.CheckFailure):
    pass


class InvalidUrl(CustomError):
    def __init__(self, argument):
        super().__init__(
            "The URL you specifed is invalid, please recheck the url."
        )
