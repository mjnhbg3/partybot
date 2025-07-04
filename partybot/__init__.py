"""PartyBot package entry point."""

from .logging import setup_logging
import discord


async def setup(bot):
    """Async entry point used by Red to load the cog."""
    if not hasattr(discord.VoiceClient, "start_recording"):
        raise RuntimeError(
            "PartyBot requires py-cord >=2.6 with voice receiving support."
        )
    from .cog import PartyBot

    await bot.add_cog(PartyBot(bot))

    setup_logging()

__all__ = ["PartyBot", "setup"]
