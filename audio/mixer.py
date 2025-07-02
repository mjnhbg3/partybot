
import numpy as np


class Mixer:
    """A real-time audio mixer."""

    def __init__(self, sample_rate: int = 48000, channels: int = 1, headroom_db: float = 6):
        self._sample_rate = sample_rate
        self._channels = channels
        self._headroom = 10 ** (-headroom_db / 20)
        self._buffer = np.zeros((0, self._channels), dtype=np.float32)

    def add(self, pcm_data: np.ndarray):
        """Adds PCM data to the mixer."""
        if pcm_data.shape[1] != self._channels:
            raise ValueError("PCM data must have the same number of channels as the mixer")

        if len(self._buffer) < len(pcm_data):
            self._buffer = np.pad(
                self._buffer,
                ((0, len(pcm_data) - len(self._buffer)), (0, 0)),
                mode="constant",
            )
        elif len(self._buffer) > len(pcm_data):
            pcm_data = np.pad(
                pcm_data,
                ((0, len(self._buffer) - len(pcm_data)), (0, 0)),
                mode="constant",
            )

        self._buffer += pcm_data

    def pop(self, duration_ms: int) -> np.ndarray:
        """Pops a chunk of mixed audio from the buffer."""
        num_frames = int(self._sample_rate * (duration_ms / 1000.0))
        if len(self._buffer) < num_frames:
            return np.zeros((0, self._channels), dtype=np.float32)

        chunk = self._buffer[:num_frames]
        self._buffer = self._buffer[num_frames:]

        # Apply headroom and clip
        chunk *= self._headroom
        np.clip(chunk, -1.0, 1.0, out=chunk)

        return chunk

    def clear(self):
        """Clears the mixer buffer."""
        self._buffer = np.zeros((0, self._channels), dtype=np.float32)
