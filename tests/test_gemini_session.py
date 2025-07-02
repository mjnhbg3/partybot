import asyncio
import types
import sys

import pytest

# Provide a minimal stub for discord.sinks.Sink used in imports
discord = sys.modules.setdefault('discord', types.ModuleType('discord'))
if not hasattr(discord, 'sinks'):
    sinks_mod = types.ModuleType('discord.sinks')

    class Sink:
        pass

    class Filters:
        @staticmethod
        def container(func):
            return func

    sinks_mod.Sink = Sink
    sinks_mod.core = types.SimpleNamespace(Filters=Filters(), AudioData=bytes)
    discord.sinks = sinks_mod
    sys.modules.setdefault('discord.sinks', sinks_mod)

import partybot.stream.gemini_session as gs_mod  # noqa: E402


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

    outputs = []

    async def run_iter():
        async for chunk in session.iter_audio():
            outputs.append(chunk)

    iter_task = asyncio.create_task(run_iter())

    await session.send_pcm(b'data')
    await asyncio.sleep(0.01)
    assert fake.sent == [b'data']

    await asyncio.sleep(0.01)
    assert outputs == [b'one', b'two']

    iter_task.cancel()
    send_task.cancel()
    await session.close()
    assert fake.closed
