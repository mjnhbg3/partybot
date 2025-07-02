
import numpy as np
import soxr


def downsample_48k_to_16k(pcm_48k: np.ndarray) -> np.ndarray:
    """Downsamples a 48kHz PCM signal to 16kHz."""
    return soxr.resample(pcm_48k, 48000, 16000, quality=soxr.FAST)


def upsample_24k_to_48k(pcm_24k: np.ndarray) -> np.ndarray:
    """Upsamples a 24kHz PCM signal to 48kHz."""
    return soxr.resample(pcm_24k, 24000, 48000, quality=soxr.FAST)
