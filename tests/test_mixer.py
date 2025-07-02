import pytest

try:
    import numpy as np
except ModuleNotFoundError:  # pragma: no cover - depends on environment
    pytest.skip("numpy is required", allow_module_level=True)
from partybot.audio.mixer import Mixer


def test_mixer_add_and_pop():
    mixer = Mixer(sample_rate=10, input_channels=1, headroom_db=0)
    pcm1 = np.full((5, 1), 0.1, dtype=np.float32)
    pcm2 = np.full((3, 1), 0.2, dtype=np.float32)
    mixer.add(user_id=1, pcm_data=pcm1)
    mixer.add(user_id=2, pcm_data=pcm2)

    chunk = mixer.pop(500)  # 5 frames at 10 Hz
    expected = np.array([0.3, 0.3, 0.3, 0.1, 0.1], dtype=np.float32)
    assert np.allclose(chunk.flatten(), expected)
    # buffer should now be empty
    assert np.allclose(mixer.pop(100), np.zeros(1))


def test_mixer_headroom_and_clear():
    mixer = Mixer(sample_rate=4, input_channels=1, headroom_db=6)
    pcm = np.full((4, 1), 1.0, dtype=np.float32)
    mixer.add(user_id=1, pcm_data=pcm)
    chunk = mixer.pop(1000)
    factor = 10 ** (-6 / 20)
    assert np.allclose(chunk.flatten(), np.ones(4) * factor)

    mixer.add(user_id=1, pcm_data=np.full((1, 1), 0.5, dtype=np.float32))
    mixer.clear()
    assert np.allclose(mixer.pop(1000), np.zeros(4))
