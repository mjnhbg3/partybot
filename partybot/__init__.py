"""PartyBot package entry point."""

from .logging import setup_logging
import discord


async def setup(bot):
    """Async entry point used by Red to load the cog."""
    missing = []
    if not hasattr(discord.VoiceClient, "start_recording"):
        missing.append("VoiceClient.start_recording")
    if not hasattr(discord, "sinks"):
        missing.append("discord.sinks")
    if getattr(discord, "version_info", (0, 0, 0)) < (2, 6):
        missing.append("py-cord>=2.6")
    if missing:
        raise RuntimeError(
            "PartyBot requires py-cord >=2.6 installed with voice receiving "
            f"support (missing: {', '.join(missing)})."
        )
    from .cog import PartyBot

    await bot.add_cog(PartyBot(bot))

    setup_logging()

__all__ = ["PartyBot", "setup"]
