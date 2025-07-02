
from __future__ import annotations

try:
    import numpy as np
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    np = None  # type: ignore[assignment]

try:
    import soxr
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    soxr = None  # type: ignore[assignment]


def downsample_48k_to_16k(pcm_48k: np.ndarray) -> np.ndarray:
    """Downsamples a 48kHz PCM signal to 16kHz."""
    if np is None or soxr is None:
        raise ModuleNotFoundError("numpy and soxr are required for resampling")
    return soxr.resample(pcm_48k, 48000, 16000, quality=soxr.FAST)


def upsample_24k_to_48k(pcm_24k: np.ndarray) -> np.ndarray:
    """Upsamples a 24kHz PCM signal to 48kHz."""
    if np is None or soxr is None:
        raise ModuleNotFoundError("numpy and soxr are required for resampling")
    return soxr.resample(pcm_24k, 24000, 48000, quality=soxr.FAST)
