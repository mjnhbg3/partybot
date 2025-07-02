
"""PartyBot package entry point."""


def setup(bot):
    from .cog import PartyBot

    bot.add_cog(PartyBot(bot))

__all__ = ["PartyBot", "setup"]
