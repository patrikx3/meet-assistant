"""Transcription engine: OpenAI GPT-4o Transcribe."""

import collections
import importlib.util
import os
import re
import tempfile
import threading

from meet_assistant import BASE_DIR

# audioop and speech_recognition are only needed for the server-side PulseAudio
# capture path (Linux workstation install). Browser capture passes WAV files
# directly, so these are deferred imports.

# ── Hallucination filter (GPT-4o transcribe ghosts on silent audio) ────────────

# Allow Latin + extended Latin scripts (covers all 10 supported European languages).
_LATIN_RE = re.compile(r'^[a-zA-Z\u00c0-\u024f\u1e00-\u1eff0-9\s\.\,\!\?\;\:\-\'\"\(\)\[\]\{\}\@\#\%\&\*\/\\\_\+\=\~\`\^\<\>\|]+$')

# Low-content single words / YouTube-style closing phrases that the model
# hallucinates on silent or music-only audio, regardless of language.
_HALLUCINATIONS = {
    "context:", "context",
    "thank you.", "thanks for watching.", "subtitle by", "subtitles by",
    "subscribe", "you", "the", "i",
    "...", ".", "", "bye.", "bye", "thank you", "thanks",
}


def _is_hallucination(text):
    t = text.strip()
    if len(t) < 3:
        return True
    if not _LATIN_RE.match(t):
        return True
    low = t.lower()
    if low in _HALLUCINATIONS:
        return True
    if low.startswith("context"):
        return True
    return False


# ── Rolling prompt context ─────────────────────────────────────────────────────

# Keep the most recent successful transcriptions; pass them as the `prompt`
# argument on each call so the model stays consistent with names, jargon, and
# speaking style. OpenAI caps the prompt at 244 tokens — we keep ~400 chars.
_CONTEXT_MAX_CHARS = 400
_context = collections.deque(maxlen=10)
_context_lock = threading.Lock()


def _build_prompt(language):
    lang_hint = f"Speech in {language}." if language else ""
    with _context_lock:
        recent = " ".join(_context)
    if not recent:
        return lang_hint or None
    # Tail-truncate to fit budget
    if len(recent) > _CONTEXT_MAX_CHARS:
        recent = recent[-_CONTEXT_MAX_CHARS:]
    return (lang_hint + " " + recent).strip() if lang_hint else recent


def _remember(text):
    with _context_lock:
        _context.append(text)


def reset_context():
    """Clear the rolling transcript context (called when user hits Clear)."""
    with _context_lock:
        _context.clear()


# ── Key resolution: env var → secure/ file ─────────────────────────────────────


def _read_key():
    """Look up the OpenAI key from env var (OPENAI_API_KEY) or secure/chatgpt."""
    val = os.environ.get("OPENAI_API_KEY")
    if val:
        return val.strip()
    path = os.path.join(BASE_DIR, "secure", "chatgpt")
    if os.path.isfile(path):
        return open(path).read().strip()
    return None


# ── Engine detection ───────────────────────────────────────────────────────────

AVAILABLE_ENGINES = {}

if importlib.util.find_spec("openai") and _read_key():
    AVAILABLE_ENGINES["openai"] = "GPT-4o Transcribe"


# ── Engine class ───────────────────────────────────────────────────────────────


class OpenAIEngine:
    def __init__(self):
        from openai import OpenAI
        key = _read_key()
        if not key:
            raise RuntimeError(
                "No OpenAI API key found. "
                "Set OPENAI_API_KEY in .env (see .env.example), "
                "or save your key to secure/chatgpt"
            )
        self.client = OpenAI(api_key=key)

    def transcribe_audio(self, audio_data, language=None):
        import audioop
        import speech_recognition as sr
        raw = audio_data.get_raw_data()
        boosted = audioop.mul(raw, audio_data.sample_width, 3.0)
        audio_data = sr.AudioData(boosted, audio_data.sample_rate, audio_data.sample_width)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_data.get_wav_data())
            p = f.name
        try:
            return self._do(p, language)
        finally:
            os.unlink(p)

    def transcribe_wav(self, path, language=None):
        return self._do(path, language)

    def _do(self, path, language):
        kwargs = {"model": "gpt-4o-transcribe"}
        if language:
            kwargs["language"] = language
        prompt = _build_prompt(language)
        if prompt:
            kwargs["prompt"] = prompt
        with open(path, "rb") as f:
            r = self.client.audio.transcriptions.create(file=f, **kwargs)
        text = r.text.strip() if r.text else None
        if not text or _is_hallucination(text):
            return None, None
        _remember(text)
        return text, language


ENGINE_CLASSES = {
    "openai": OpenAIEngine,
}
