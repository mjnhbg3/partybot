
import asyncio
import contextlib
import google.generativeai as genai
from partybot.utils.backpressure import BackpressureQueue


class GeminiSession:
    """A wrapper around the Google Generative AI LiveSession."""

    def __init__(self, api_key: str, model_id: str, proactive_audio: bool = True):
        self._api_key = api_key
        self._model_id = model_id
        self._proactive_audio = proactive_audio
        self._session = None
        self.in_q = BackpressureQueue(maxsize=100)  # 10 seconds of audio
        self.out_q = BackpressureQueue(maxsize=100)

    async def create(self):
        """Creates the LiveSession."""
        genai.configure(api_key=self._api_key)
        self._session = await genai.live_session(
            model=self._model_id,
            audio_config={
                "encoding": "LINEAR16",
                "sample_rate_hertz": 16000,
                "channels": 1,
            },
            response_modalities=["AUDIO"],
            proactivity={"proactive_audio": self._proactive_audio},
        )

    async def send_pcm(self, pcm_data: bytes):
        """Sends PCM data to the LiveSession."""
        if self._session:
            await self.in_q.put(pcm_data)

    async def iter_audio(self):
        """Yields audio bytes produced by the LiveSession."""
        if not self._session:
            return

        async def _recv_loop():
            async for chunk in self._session.response_iter():
                if chunk.audio:
                    await self.out_q.put(chunk.audio)

        recv_task = asyncio.create_task(_recv_loop())

        try:
            while self._session:
                chunk = await self.out_q.get()
                yield chunk
        finally:
            recv_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await recv_task

    async def close(self):
        """Closes the LiveSession."""
        if self._session:
            await self._session.close()
            self._session = None

    async def _send_loop(self):
        """The loop that sends audio to the LiveSession."""
        while self._session:
            pcm_data = await self.in_q.get()
            if self._session:
                await self._session.send(pcm_data)

    def start_send_loop(self):
        """Starts the send loop."""
        asyncio.create_task(self._send_loop())
