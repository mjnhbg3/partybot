
from .cog import PartyBot


def setup(bot):
    bot.add_cog(PartyBot(bot))
