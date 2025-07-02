import numpy as np
from partybot.audio.mixer import Mixer


def test_mixer_add_and_pop():
    mixer = Mixer(sample_rate=10, channels=1, headroom_db=0)
    pcm1 = np.full((5, 1), 0.1, dtype=np.float32)
    pcm2 = np.full((3, 1), 0.2, dtype=np.float32)
    mixer.add(pcm1, user_id=0)
    mixer.add(pcm2, user_id=1)

    chunk = mixer.pop(500)  # 5 frames at 10 Hz
    expected = np.array([0.3, 0.3, 0.3, 0.1, 0.1], dtype=np.float32)
    assert np.allclose(chunk.flatten(), expected)
    # buffer should now be empty
    assert mixer.pop(100).shape[0] == 0


def test_mixer_headroom_and_clear():
    mixer = Mixer(sample_rate=4, channels=1, headroom_db=6)
    pcm = np.full((4, 1), 1.0, dtype=np.float32)
    mixer.add(pcm, user_id=0)
    chunk = mixer.pop(1000)
    factor = 10 ** (-6 / 20)
    assert np.allclose(chunk.flatten(), np.ones(4) * factor)

    mixer.add(np.full((1, 1), 0.5, dtype=np.float32), user_id=0)
    mixer.clear()
    assert mixer.pop(1000).size == 0
