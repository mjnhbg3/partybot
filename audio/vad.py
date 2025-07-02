
import webrtcvad
import numpy as np


class VAD:
    """A wrapper around webrtcvad to detect speech in audio frames."""

    def __init__(self, sample_rate: int = 16000, frame_duration_ms: int = 20):
        self._vad = webrtcvad.Vad()
        self._sample_rate = sample_rate
        self._frame_duration_ms = frame_duration_ms
        self._frame_size = int(
            self._sample_rate * (self._frame_duration_ms / 1000.0) * 2
        )  # 16-bit PCM

    def is_speech(
        self, frame: bytes, threshold: float = -float("inf")
    ) -> bool:
        """Return True if the frame is speech above the given threshold."""
        if len(frame) != self._frame_size:
            raise ValueError(f"Frame must be {self._frame_size} bytes")

        if threshold > -float("inf"):
            pcm = (
                np.frombuffer(frame, dtype=np.int16).astype(np.float32)
                / 32768.0
            )
            rms = np.sqrt(np.mean(pcm ** 2))
            level_db = -np.inf if rms == 0 else 20 * np.log10(rms)
            if level_db < threshold:
                return False

        return self._vad.is_speech(frame, self._sample_rate)
