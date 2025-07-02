
import asyncio
import io
from typing import AsyncIterator, Tuple

import discord
import numpy as np


class _FrameReceiver(discord.sinks.Sink):
    """Sink that forwards PCM frames to an asyncio queue."""

    def __init__(self, loop: asyncio.AbstractEventLoop):
        super().__init__()
        self.loop = loop
        self.queue: asyncio.Queue[Tuple[int, bytes]] = asyncio.Queue()

    @discord.sinks.core.Filters.container  # type: ignore[attr-defined]
    def write(self, data: bytes, user: int):  # pragma: no cover - runs in thread
        # Called in a separate thread by py-cord
        self.loop.call_soon_threadsafe(self.queue.put_nowait, (user, data))

    def format_audio(self, audio: discord.sinks.core.AudioData):  # type: ignore
        # Override to avoid writing files
        pass


class DiscordBridge:
    """A bridge between Discord's voice client and the bot's audio processing pipeline."""

    def __init__(self, vc: discord.VoiceClient):
        self._vc = vc
        self._receiver = _FrameReceiver(vc.loop)
        self._vc.start_recording(self._receiver, self._on_record_finish)

    async def recv_frames(self) -> AsyncIterator[Tuple[int, np.ndarray]]:
        """Receives audio frames from Discord."""
        while self._vc.is_connected():
            user_id, pcm_data = await self._receiver.queue.get()
            yield user_id, self._to_float(pcm_data)

    async def play_pcm(self, pcm_data: np.ndarray):
        """Plays PCM data to Discord."""
        if self._vc.is_playing():
            # This is a simple approach. A more robust solution would be to queue the audio.
            return

        pcm_bytes = self._to_s16le(pcm_data)
        self._vc.play(discord.PCMAudio(io.BytesIO(pcm_bytes)))

    async def _on_record_finish(self, sink: _FrameReceiver):
        """Callback for when recording stops."""
        pass

    def _to_float(self, pcm_data: bytes) -> np.ndarray:
        """Converts s16le PCM data to float32."""
        array = np.frombuffer(pcm_data, dtype=np.int16).astype(np.float32) / 32768.0
        return array.reshape(-1, 1)

    def _to_s16le(self, pcm_data: np.ndarray) -> bytes:
        """Converts float32 PCM data to stereo s16le."""
        if pcm_data.ndim == 1:
            pcm_data = pcm_data.reshape(-1, 1)
        if pcm_data.shape[1] == 1:
            pcm_data = np.repeat(pcm_data, 2, axis=1)
        return (pcm_data * 32768.0).astype(np.int16).tobytes()
