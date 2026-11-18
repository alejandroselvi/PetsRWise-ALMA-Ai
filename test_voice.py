import unittest
from types import SimpleNamespace
from alma_voice import (transcribe_recording, synthesize_reply,
                        speech_instructions, DEFAULT_SPEED, DEFAULT_VOICE)


class Recording:
    def getvalue(self): return b'RIFF' + b'0' * 20


class FakeTranscriptions:
    def create(self, **kwargs):
        self.kwargs = kwargs
        return SimpleNamespace(text='  hola ALMA  ')


class FakeSpeech:
    def create(self, **kwargs):
        self.kwargs = kwargs
        return SimpleNamespace(content=b'fake_mp3')


class TestVoice(unittest.TestCase):
    def test_transcribe_es(self):
        api = FakeTranscriptions()
        client = SimpleNamespace(audio=SimpleNamespace(transcriptions=api))
        self.assertEqual(transcribe_recording(client, Recording(), 'Español'), 'hola ALMA')
        self.assertEqual(api.kwargs['language'], 'es')

    def test_voice_spanish_latam_and_speed(self):
        api = FakeSpeech()
        client = SimpleNamespace(audio=SimpleNamespace(speech=api))
        self.assertEqual(synthesize_reply(client, 'Hola', 'Español'), b'fake_mp3')
        self.assertEqual(api.kwargs['voice'], DEFAULT_VOICE)
        self.assertEqual(api.kwargs['speed'], DEFAULT_SPEED)
        self.assertIn('latinoamericano', api.kwargs['instructions'])
        self.assertEqual(api.kwargs['response_format'], 'mp3')

    def test_american_english(self):
        api = FakeSpeech()
        client = SimpleNamespace(audio=SimpleNamespace(speech=api))
        synthesize_reply(client, 'Hello', 'English', voice='coral', speed=1.35)
        self.assertEqual(api.kwargs['voice'], 'coral')
        self.assertEqual(api.kwargs['speed'], 1.35)
        self.assertIn('United States English', api.kwargs['instructions'])

    def test_empty(self):
        api = FakeSpeech()
        client = SimpleNamespace(audio=SimpleNamespace(speech=api))
        with self.assertRaises(ValueError): synthesize_reply(client, ' ')

    def test_invalid_voice(self):
        api = FakeSpeech()
        client = SimpleNamespace(audio=SimpleNamespace(speech=api))
        with self.assertRaises(ValueError): synthesize_reply(client, 'Hello', voice='unknown')

    def test_invalid_speed(self):
        api = FakeSpeech()
        client = SimpleNamespace(audio=SimpleNamespace(speech=api))
        with self.assertRaises(ValueError): synthesize_reply(client, 'Hola', speed=4.0)

    def test_instructions(self):
        self.assertIn('sin acento de España', speech_instructions('Español'))
        self.assertIn('General American', speech_instructions('English'))

if __name__ == '__main__': unittest.main()
