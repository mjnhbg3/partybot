import numpy as np
import types
import sys

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

from partybot.voice.discord_bridge import DiscordBridge


def test_to_float_preserves_channels():
    bridge = object.__new__(DiscordBridge)
    pcm = np.array([0, 32767, -32768, 16384], dtype=np.int16).tobytes()
    result = bridge._to_float(pcm)
    assert result.shape == (2, 2)
    expected = np.array(
        [[0.0, 32767 / 32768.0], [-1.0, 16384 / 32768.0]], dtype=np.float32
    )
    assert np.allclose(result, expected)
