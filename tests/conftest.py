import os
import sys
import types

# Avoid shadowing the stdlib logging module
root = sys.path.pop(0)
import logging as builtin_logging  # noqa: E402
sys.modules['logging'] = builtin_logging
sys.path.insert(0, root)

# Ensure the project package can be imported as 'partybot'
repo_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(repo_root))

# Provide minimal stubs for external dependencies used during imports
# Discord stub with basic classes
discord_stub = types.ModuleType('discord')


class VoiceClient:
    pass


class AudioSink:
    pass


class PCMAudio:
    def __init__(self, data):
        self.data = data


discord_stub.VoiceClient = VoiceClient
discord_stub.AudioSink = AudioSink
discord_stub.PCMAudio = PCMAudio
discord_stub.sinks = types.SimpleNamespace(
    Sink=type('Sink', (), {}),
    core=types.SimpleNamespace(
        Filters=types.SimpleNamespace(container=lambda f: f)
    ),
)
discord_stub.sinks.core.AudioData = bytes
sys.modules.setdefault('discord', discord_stub)

for name in [
    'redbot',
    'redbot.core',
    'redbot.core.commands',
    'google',
    'google.generativeai',
]:
    if name not in sys.modules:
        sys.modules[name] = types.ModuleType(name)

# Commands stub
actions = sys.modules['redbot.core.commands']
if not hasattr(actions, 'Cog'):

    class Cog:
        pass

    class Context:
        pass

    def command(*d, **k):
        def deco(f):
            return f
        return deco

    def group(*d, **k):
        def deco(f):
            f.command = command
            return f
        return deco
    actions.Cog = Cog
    actions.Context = Context
    actions.group = group
    actions.command = command

# Config stub used in cog imports
core = sys.modules.get('redbot.core')
if core and not hasattr(core, 'Config'):
    class DummyConfig:
        def get_conf(self, *a, **k):
            return self

        def register_guild(self, *a, **k):
            pass

        def guild(self, *a, **k):
            class Dummy:
                async def all(self):
                    return {}
            return Dummy()
    core.Config = DummyConfig
