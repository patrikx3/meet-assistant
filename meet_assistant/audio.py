"""Audio device utilities and suppressed speech_recognition import."""

import os
import subprocess

HAS_AUDIO = False
sr = None


def _suppress_stderr():
    """Redirect stderr to /dev/null at OS level (silences ALSA/Jack/PulseAudio messages)."""
    devnull = os.open(os.devnull, os.O_WRONLY)
    old_stderr = os.dup(2)
    os.dup2(devnull, 2)
    os.close(devnull)
    return old_stderr


def _restore_stderr(old_stderr):
    os.dup2(old_stderr, 2)
    os.close(old_stderr)


# Import speech_recognition with stderr suppressed (ALSA/Jack spam).
# On cloud servers without PyAudio, this gracefully skips.
try:
    _old = _suppress_stderr()
    import speech_recognition as sr
    _restore_stderr(_old)
    HAS_AUDIO = True
except ImportError:
    try:
        _restore_stderr(_old)
    except Exception:
        pass


def find_monitor_source():
    """Find the PulseAudio/PipeWire monitor source to capture speaker output."""
    result = subprocess.run(["pactl", "list", "short", "sources"], capture_output=True, text=True)
    for line in result.stdout.splitlines():
        if ".monitor" in line:
            return line.split()[1]
    return None
