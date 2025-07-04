"""PartyBot package entry point."""

from .logging import setup_logging


async def setup(bot):
    """Async entry point used by Red to load the cog."""
    from .cog import PartyBot

    await bot.add_cog(PartyBot(bot))

    setup_logging()

__all__ = ["PartyBot", "setup"]
