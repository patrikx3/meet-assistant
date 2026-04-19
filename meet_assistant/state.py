"""Application state, WebSocket broadcasting, audio capture loop, and control functions."""

import asyncio
import os
import tempfile
import threading
import time
from datetime import datetime

from meet_assistant import BASE_DIR, diarizer
from meet_assistant import engines
from meet_assistant.engines import AVAILABLE_ENGINES, ENGINE_CLASSES

# ── Session auto-save ─────────────────────────────────────────────────────────

_SESSIONS_DIR = os.path.join(BASE_DIR, "sessions")
_session_file = None
_session_lock = threading.Lock()


def _session_path():
    """Return the current session's file path, creating a new one per day-hour-minute."""
    global _session_file
    with _session_lock:
        if _session_file is None:
            os.makedirs(_SESSIONS_DIR, exist_ok=True)
            stamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
            _session_file = os.path.join(_SESSIONS_DIR, f"{stamp}.txt")
        return _session_file


def _append_to_session(line):
    try:
        path = _session_path()
        with open(path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass  # Never let session-save errors break transcription


def _reset_session_file():
    global _session_file
    with _session_lock:
        _session_file = None

# ── Mutable state ──────────────────────────────────────────────────────────────

loop = None
clients = set()
current_engine = None
current_engine_name = None

# Supported transcription languages. One per session to avoid cross-language
# hallucinations. Native names shown in UI.
SUPPORTED_LANGUAGES = {
    "en": "English",
    "hu": "Magyar",
    "de": "Deutsch",
    "fr": "Fran\u00e7ais",
    "es": "Espa\u00f1ol",
    "it": "Italiano",
    "pt": "Portugu\u00eas",
    "nl": "Nederlands",
    "pl": "Polski",
    "cs": "\u010ce\u0161tina",
}
current_language = "en"
server_capture = False  # True when PulseAudio capture is active (localhost mode)
speaker_stop = threading.Event()

# ── Broadcasting ───────────────────────────────────────────────────────────────


async def _broadcast(data):
    dead = set()
    for ws in list(clients):
        try:
            await ws.send_json(data)
        except Exception:
            dead.add(ws)
    clients.difference_update(dead)


def broadcast(data):
    if loop and clients:
        asyncio.run_coroutine_threadsafe(_broadcast(data), loop)


_recent = []  # dedup buffer: (timestamp, text)


def send_transcript(text, lang=None, speaker=None):
    now = time.time()
    for ts, prev in _recent:
        if now - ts < 3 and prev == text:
            return
    _recent.append((now, text))
    _recent[:] = [(ts, t) for ts, t in _recent if now - ts < 5]

    stamp = datetime.now().strftime("%H:%M:%S")
    broadcast({
        "type": "transcript",
        "speaker": speaker,
        "text": text,
        "lang": lang.upper() if lang else None,
        "time": stamp,
    })

    # Auto-save to disk
    spk_label = f"Speaker {speaker}" if speaker else "Speaker"
    lang_tag = f" [{lang.upper()}]" if lang else ""
    _append_to_session(f"[{stamp}] {spk_label}{lang_tag}: {text}")


def send_status(status):
    broadcast({"type": "status", "status": status})


def send_state():
    broadcast({
        "type": "state",
        "engine": current_engine_name,
        "engines": AVAILABLE_ENGINES,
        "language": current_language,
        "languages": SUPPORTED_LANGUAGES,
    })


# ── Diarization helpers ────────────────────────────────────────────────────────


def _audio_data_to_wav_bytes(audio_data):
    """Convert a speech_recognition AudioData into raw WAV bytes."""
    import speech_recognition as sr
    raw = audio_data.get_raw_data()
    return sr.AudioData(raw, audio_data.sample_rate, audio_data.sample_width).get_wav_data()


def _diarize(wav_bytes):
    try:
        return diarizer.identify_speaker(wav_bytes)
    except Exception:
        return None


# ── Capture loop ───────────────────────────────────────────────────────────────


def speaker_capture_loop(recognizer, speaker):
    """Capture speaker audio via PulseAudio monitor and transcribe."""
    from meet_assistant.audio import _suppress_stderr, _restore_stderr
    import speech_recognition as sr

    while not speaker_stop.is_set():
        try:
            send_status("listening")
            old_err = _suppress_stderr()
            try:
                with speaker as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = recognizer.listen(source, timeout=10, phrase_time_limit=30)
            finally:
                _restore_stderr(old_err)
        except sr.WaitTimeoutError:
            continue
        except Exception:
            time.sleep(1)
            continue

        engine = current_engine
        if not engine:
            continue
        send_status("processing")
        try:
            text, lang = engine.transcribe_audio(audio, language=current_language)
            if text:
                spk = _diarize(_audio_data_to_wav_bytes(audio))
                send_transcript(text, lang or current_language, speaker=spk)
        except Exception as e:
            broadcast({"type": "error", "error": str(e)})


# ── Control functions ──────────────────────────────────────────────────────────


def set_language(lang):
    global current_language
    if lang not in SUPPORTED_LANGUAGES:
        return
    current_language = lang
    send_state()


def reset_speakers():
    """Clear diarizer memory, rolling prompt context, and start a new session file."""
    diarizer.reset()
    engines.reset_context()
    _reset_session_file()


def transcribe_browser_audio(wav_bytes):
    """Transcribe WAV audio received from browser capture (getUserMedia / getDisplayMedia)."""
    engine = current_engine
    if not engine:
        return
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(wav_bytes)
        p = f.name
    try:
        text, lang = engine.transcribe_wav(p, language=current_language)
        if text:
            spk = _diarize(wav_bytes)
            send_transcript(text, lang or current_language, speaker=spk)
    except Exception as e:
        broadcast({"type": "error", "error": str(e)})
    finally:
        os.unlink(p)
