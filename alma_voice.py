"""ALMA voice synthesis for internal demo only. Not realtime, not a human voice."""
from __future__ import annotations

from io import BytesIO

# A consistent synthetic voice can be used in both languages.
# The audio endpoint supports explicit speed and accent instructions.
VOICE_OPTIONS = ('marin', 'coral', 'shimmer')
DEFAULT_VOICE = 'marin'
DEFAULT_SPEED = 1.20


def transcribe_recording(client, recorded, language: str = 'Español') -> str:
    """Transcribe an audio question. Do not store real patient recordings here."""
    data = recorded.getvalue()
    if not data:
        raise ValueError('Empty audio recording')
    if len(data) > 15 * 1024 * 1024:
        raise ValueError('Recording too large for this demo')
    upload = BytesIO(data)
    upload.name = 'alma_voice_question.wav'
    response = client.audio.transcriptions.create(
        model='gpt-transcribe',
        file=upload,
        language='es' if language == 'Español' else 'en',
    )
    return (response.text or '').strip()


def speech_instructions(language: str) -> str:
    """Pronunciation direction, not a guarantee of an exact regional accent."""
    if language == 'Español':
        return (
            'Habla EXCLUSIVAMENTE en español latinoamericano neutro; pronunciación de América Latina, '
            'sin acento de España y sin ceceo peninsular. Voz natural, cálida, profesional y accesible. '
            'Ritmo ágil y conversacional, pronunciación precisa de nombres y términos veterinarios. '
            'Haz pausas breves tras ideas importantes y pronuncia las advertencias de emergencia con mucha claridad. '
            'No inventes contenido y no cambies las palabras proporcionadas.'
        )
    return (
        'Speak in natural United States English with a neutral General American accent. '
        'Avoid British or other non-US English accents. Use a warm, confident, approachable, '
        'professional, brisk conversational delivery with clear pronunciation of veterinary terms. '
        'Pause briefly for important safety warnings. Do not change the provided text.'
    )


def synthesize_reply(client, text: str, language: str = 'Español',
                     voice: str = DEFAULT_VOICE, speed: float = DEFAULT_SPEED) -> bytes:
    """Generate MP3 in Spanish (LatAm) or English (US) at chosen speaking rate.

    `speed` is sent to the OpenAI Speech API; this is audio generation, not a
    client-side audio-player speed hack. The result is synthetic speech.
    """
    if not text or not text.strip():
        raise ValueError('Empty speech text')
    if voice not in VOICE_OPTIONS:
        raise ValueError('Unsupported voice selection')
    speed = float(speed)
    if not 0.80 <= speed <= 1.60:
        raise ValueError('Supported UI speech speed is from 0.80x to 1.60x')
    response = client.audio.speech.create(
        model='gpt-4o-mini-tts',
        voice=voice,
        input=text[:3000],
        instructions=speech_instructions(language),
        speed=speed,
        response_format='mp3',
    )
    return response.content
