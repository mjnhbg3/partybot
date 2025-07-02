
import asyncio
import discord
import numpy as np
from typing import AsyncIterator, Tuple


class DiscordBridge:
    """A bridge between Discord's voice client and the bot's audio processing pipeline."""

    def __init__(self, vc: discord.VoiceClient):
        self._vc = vc
        self._vc.listen(self._sink())

    async def recv_frames(self) -> AsyncIterator[Tuple[int, np.ndarray]]:
        """Receives audio frames from Discord."""
        while self._vc.is_connected():
            try:
                user_id, pcm_data = await self._vc.recv_audio()
                yield user_id, self._to_float(pcm_data)
            except asyncio.TimeoutError:
                continue

    async def play_pcm(self, pcm_data: np.ndarray):
        """Plays PCM data to Discord."""
        if self._vc.is_playing():
            # This is a simple approach. A more robust solution would be to queue the audio.
            return

        pcm_bytes = self._to_s16le(pcm_data)
        self._vc.play(discord.PCMAudio(pcm_bytes))

    def _sink(self):
        """A sink to discard incoming audio packets until recv_audio is called."""

        class SilenceSink(discord.AudioSink):
            def write(self, data, user_id):
                pass

        return SilenceSink()

    def _to_float(self, pcm_data: bytes) -> np.ndarray:
        """Converts s16le PCM data to float32."""
        return np.frombuffer(pcm_data, dtype=np.int16).astype(np.float32) / 32768.0

    def _to_s16le(self, pcm_data: np.ndarray) -> bytes:
        """Converts float32 PCM data to s16le."""
        return (pcm_data * 32768.0).astype(np.int16).tobytes()
