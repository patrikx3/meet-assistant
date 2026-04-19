"""Meet Assistant — package init.

When running from source (`./meet-assistant-web.py`), BASE_DIR points at the
project root. When installed via pip, BASE_DIR points at the current working
directory, so the user's `.env` and `secure/` folder are picked up from wherever
they invoked `p3x-meet-assistant`.
"""

import os

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
# Parent of package dir — the project root when running from source.
_source_root = os.path.dirname(PACKAGE_DIR)
# When installed (site-packages), _source_root won't contain project files —
# fall back to cwd so users can keep .env/secure/ in their working directory.
_source_marker = os.path.join(_source_root, "pyproject.toml")
BASE_DIR = _source_root if os.path.isfile(_source_marker) else os.getcwd()

# Auto-load .env — first from BASE_DIR, then search upward from cwd as a fallback.
try:
    from dotenv import load_dotenv
    env_path = os.path.join(BASE_DIR, ".env")
    if os.path.isfile(env_path):
        load_dotenv(env_path)
    else:
        load_dotenv()  # Walk upward from cwd
except Exception:
    pass

# Import audio first so speech_recognition is loaded with ALSA/Jack messages suppressed.
# On cloud servers without PyAudio, this gracefully sets HAS_AUDIO=False.
from . import audio as _audio
HAS_AUDIO = _audio.HAS_AUDIO
