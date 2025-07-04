
"""PartyBot package entry point."""

from .logging import setup_logging


def setup(bot):
    from .cog import PartyBot

    bot.add_cog(PartyBot(bot))


setup_logging()

__all__ = ["PartyBot", "setup"]
