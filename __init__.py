
def setup(bot):
    from .cog import PartyBot

    bot.add_cog(PartyBot(bot))
