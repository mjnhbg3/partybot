import asyncio
import types

import pytest

import partybot.stream.gemini_session as gs_mod


class FakeChunk:
    def __init__(self, audio):
        self.audio = audio


class FakeLiveSession:
    def __init__(self, responses):
        self.sent = []
        self.responses = responses
        self.closed = False

    async def send(self, data):
        self.sent.append(data)

    async def response_iter(self):
        for resp in self.responses:
            yield FakeChunk(resp)

    async def close(self):
        self.closed = True


@pytest.mark.asyncio
async def test_gemini_session_send_receive(monkeypatch):
    fake = FakeLiveSession([b'one', b'two'])

    async def fake_live_session(**kwargs):
        return fake

    monkeypatch.setattr(gs_mod.genai, 'configure', lambda api_key: None, raising=False)
    monkeypatch.setattr(gs_mod.genai, 'live_session', fake_live_session, raising=False)

    session = gs_mod.GeminiSession(api_key='k', model_id='m')
    await session.create()
    send_task = asyncio.create_task(session._send_loop())

    async def collect_audio(n=2):
        out = []
        async for chunk in session.iter_audio():
            out.append(chunk)
            if len(out) >= n:
                break
        return out

    iter_task = asyncio.create_task(collect_audio())

    await session.send_pcm(b'data')
    await asyncio.sleep(0.01)
    assert fake.sent == [b'data']

    results = await asyncio.wait_for(iter_task, timeout=1)
    assert results == [b'one', b'two']

    send_task.cancel()
    await session.close()
    assert fake.closed
