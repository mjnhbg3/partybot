import asyncio

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

    monkeypatch.setattr(
        gs_mod.genai, 'configure', lambda api_key: None, raising=False
    )
    monkeypatch.setattr(
        gs_mod.genai, 'live_session', fake_live_session, raising=False
    )

    session = gs_mod.GeminiSession(api_key='k', model_id='m')
    await session.create()
    send_task = asyncio.create_task(session._send_loop())
    iter_task = asyncio.create_task(session.iter_audio())

    await session.send_pcm(b'data')
    await asyncio.sleep(0.01)
    assert fake.sent == [b'data']

    out1 = await asyncio.wait_for(session.out_q.get(), timeout=1)
    out2 = await asyncio.wait_for(session.out_q.get(), timeout=1)
    assert out1 == b'one' and out2 == b'two'

    iter_task.cancel()
    send_task.cancel()
    await session.close()
    assert fake.closed
