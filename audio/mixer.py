import numpy as np
from collections import deque
from typing import Dict


class Mixer:
    """A real-time audio mixer that keeps per-user ring buffers."""

    def __init__(
        self,
        sample_rate: int = 48000,
        input_channels: int = 2,
        headroom_db: float = 6,
        buffer_ms: int = 1000,
    ):
        self._sample_rate = sample_rate
        self._input_channels = input_channels
        self._headroom = 10 ** (-headroom_db / 20)
        self._frame_capacity = int(self._sample_rate * (buffer_ms / 1000.0))
        self._buffers: Dict[int, deque[np.ndarray]] = {}

    def _to_mono(self, pcm_data: np.ndarray) -> np.ndarray:
        """Converts incoming audio to mono float32."""
        pcm = np.asarray(pcm_data, dtype=np.float32)
        if pcm.ndim == 1:
            if self._input_channels > 1:
                if len(pcm) % self._input_channels != 0:
                    raise ValueError("PCM length must be divisible by number of channels")
                pcm = pcm.reshape(-1, self._input_channels)
            else:
                pcm = pcm.reshape(-1, 1)
        elif pcm.shape[1] != self._input_channels:
            raise ValueError("PCM data must have the same number of channels as the mixer")
        return pcm.mean(axis=1)

    def add(self, user_id: int, pcm_data: np.ndarray):
        """Adds PCM data from a user to the mixer."""
        mono = self._to_mono(pcm_data)
        if user_id not in self._buffers:
            self._buffers[user_id] = deque()
        self._buffers[user_id].append(mono)

        total = sum(len(chunk) for chunk in self._buffers[user_id])
        while total > self._frame_capacity and self._buffers[user_id]:
            removed = self._buffers[user_id].popleft()
            total -= len(removed)

    def pop(self, duration_ms: int) -> np.ndarray:
        """Pops a chunk of mixed mono audio from the buffers."""
        num_frames = int(self._sample_rate * (duration_ms / 1000.0))
        if num_frames <= 0:
            return np.zeros(0, dtype=np.float32)

        mixed = np.zeros(num_frames, dtype=np.float32)
        for dq in self._buffers.values():
            frames_needed = num_frames
            parts = []
            while frames_needed > 0 and dq:
                chunk = dq[0]
                if len(chunk) <= frames_needed:
                    parts.append(chunk)
                    dq.popleft()
                    frames_needed -= len(chunk)
                else:
                    parts.append(chunk[:frames_needed])
                    dq[0] = chunk[frames_needed:]
                    frames_needed = 0

            if parts:
                user_mix = np.concatenate(parts)
                if len(user_mix) < num_frames:
                    user_mix = np.pad(user_mix, (0, num_frames - len(user_mix)))
                mixed += user_mix

        mixed *= self._headroom
        np.clip(mixed, -1.0, 1.0, out=mixed)
        return mixed

    def clear(self):
        """Clears all mixer buffers."""
        self._buffers.clear()
