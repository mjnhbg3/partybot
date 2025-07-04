import pytest
from partybot.audio.vad import VAD


def test_vad_is_speech(monkeypatch):
    vad = VAD()
    called = {}

    def fake_is_speech(frame, sample_rate):
        called['frame'] = frame
        called['rate'] = sample_rate
        return True

    monkeypatch.setattr(vad._vad, 'is_speech', fake_is_speech)
    frame = b'\x00' * vad._frame_size
    assert vad.is_speech(frame)
    assert called['frame'] == frame
    assert called['rate'] == vad._sample_rate


def test_vad_frame_size_validation():
    vad = VAD()
    with pytest.raises(ValueError):
        vad.is_speech(b'\x00' * (vad._frame_size - 1))
