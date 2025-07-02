
import webrtcvad


class VAD:
    """A wrapper around webrtcvad to detect speech in audio frames."""

    def __init__(self, sample_rate: int = 16000, frame_duration_ms: int = 20):
        self._vad = webrtcvad.Vad()
        self._sample_rate = sample_rate
        self._frame_duration_ms = frame_duration_ms
        self._frame_size = int(
            self._sample_rate * (self._frame_duration_ms / 1000.0) * 2
        )  # 16-bit PCM

    def is_speech(self, frame: bytes, threshold: float = 0.5) -> bool:
        """Returns True if the frame contains speech."""
        if len(frame) != self._frame_size:
            raise ValueError(f"Frame must be {self._frame_size} bytes")
        return self._vad.is_speech(frame, self._sample_rate)
