#!/usr/bin/env python3
"""Dev-mode launcher. For production install via pip + run `p3x-meet-assistant`.

This script auto-activates the project venv and installs missing packages,
then hands off to the same `meet_assistant.cli:main` entry point that the
installed console script uses.
"""

import os
import subprocess
import sys


def ensure_venv():
    venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "bin", "python3")
    if os.path.isfile(venv_python) and os.path.abspath(sys.executable) != os.path.abspath(venv_python):
        os.execv(venv_python, [venv_python] + sys.argv)


def ensure_packages():
    required = {"fastapi": "fastapi", "uvicorn": "uvicorn", "websockets": "websockets", "openai": "openai"}
    for module, pip_name in required.items():
        try:
            __import__(module)
        except ImportError:
            print(f"Installing {pip_name}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
    # Optional: audio capture packages (only needed for server-side PulseAudio capture)
    for module, pip_name in {"speech_recognition": "SpeechRecognition", "pyaudio": "PyAudio"}.items():
        try:
            __import__(module)
        except ImportError:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name],
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass


if __name__ == "__main__":
    ensure_venv()
    ensure_packages()
    from meet_assistant.cli import main
    main()
