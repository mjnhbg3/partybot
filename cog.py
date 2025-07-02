
import asyncio
from typing import Optional

import discord
from redbot.core import commands, Config

from partybot.audio.mixer import Mixer
from partybot.audio.resample import downsample_48k_to_16k, upsample_24k_to_48k
from partybot.audio.vad import VAD
from partybot.stream.gemini_session import GeminiSession
from partybot.voice.discord_bridge import DiscordBridge
from partybot.logging import get_logger


class PartyBot(commands.Cog):
    """Real-time voice chat with Gemini."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        default_guild = {
            "model_id": "gemini-2.5-flash-preview-native-audio-dialog",
            "input_buffer_ms": 100,
            "silence_level_db": -45,
            "mix_headroom_db": 6,
            "voice_name": "aura-asteria-en",
            "cost_guard_usd": 2.0,
        }
        self.config.register_guild(**default_guild)
        self.active_sessions: dict[int, asyncio.Task] = {}
        self.logger = get_logger(__name__)

    @commands.group()
    async def partybot(self, ctx: commands.Context):
        """Manage the PartyBot."""
        pass

    @partybot.command()
    async def join(self, ctx: commands.Context):
        """Joins the voice channel you are in."""
        if not ctx.author.voice:
            await ctx.send("You must be in a voice channel to use this command.")
            return

        channel = ctx.author.voice.channel
        if ctx.voice_client and ctx.voice_client.is_connected():
            await ctx.send("I am already in a voice channel.")
            return

        if ctx.guild.id in self.active_sessions:
            await ctx.send("I am already running in this guild.")
            return

        self.active_sessions[ctx.guild.id] = asyncio.create_task(
            self._voice_session(ctx)
        )
        await ctx.send(f"Joining {channel.name}.")

    @partybot.command()
    async def leave(self, ctx: commands.Context):
        """Leaves the voice channel."""
        if not ctx.voice_client:
            await ctx.send("I am not in a voice channel.")
            return

        if ctx.guild.id in self.active_sessions:
            self.active_sessions[ctx.guild.id].cancel()
            del self.active_sessions[ctx.guild.id]

        await ctx.voice_client.disconnect()
        await ctx.send("Leaving the voice channel.")

    async def _voice_session(self, ctx: commands.Context):
        """The main voice session loop."""
        try:
            vc = await ctx.author.voice.channel.connect(cls=discord.VoiceClient)
            bridge = DiscordBridge(vc)

            guild_config = await self.config.guild(ctx.guild).all()
            gemini_session = GeminiSession(
                api_key=await self.bot.get_shared_api_tokens("google").get("api_key"),
                model_id=guild_config["model_id"],
            )
            await gemini_session.create()
            gemini_session.start_send_loop()

            mixer = Mixer(headroom_db=guild_config["mix_headroom_db"])
            vad = VAD()

            capture_task = asyncio.create_task(self._capture_loop(bridge, gemini_session, mixer, vad, guild_config))
            playback_task = asyncio.create_task(self._playback_loop(bridge, gemini_session))

            await asyncio.gather(capture_task, playback_task)

        except asyncio.CancelledError:
            self.logger.info(f"Voice session in {ctx.guild.name} cancelled.")
        except Exception as e:
            self.logger.error(f"Error in voice session: {e}", exc_info=True)
            await ctx.send("An error occurred during the voice session.")
        finally:
            if vc and vc.is_connected():
                await vc.disconnect()
            if gemini_session:
                await gemini_session.close()

    async def _capture_loop(
        self,
        bridge: DiscordBridge,
        gemini_session: GeminiSession,
        mixer: Mixer,
        vad: VAD,
        guild_config: dict,
    ):
        """The loop that captures audio from Discord and sends it to Gemini."""
        async for user_id, pcm48 in bridge.recv_frames():
            mixer.add(pcm48)

            chunk = mixer.pop(guild_config["input_buffer_ms"])
            if chunk.size > 0:
                chunk16 = downsample_48k_to_16k(chunk)
                if vad.is_speech(chunk16.tobytes(), threshold=guild_config["silence_level_db"]):
                    await gemini_session.send_pcm(chunk16.tobytes())

    async def _playback_loop(self, bridge: DiscordBridge, gemini_session: GeminiSession):
        """The loop that plays audio from Gemini back to Discord."""
        async for chunk24 in gemini_session.iter_audio():
            pcm48 = upsample_24k_to_48k(chunk24)
            await bridge.play_pcm(pcm48)
