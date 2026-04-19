"""Meet Assistant CLI entry point — used both by the `p3x-meet-assistant` console
script (when pip-installed) and by the top-level ./meet-assistant-web.py launcher
(for git-clone dev workflow)."""

import argparse
import os
import sys
import threading

import uvicorn

import meet_assistant.state as state
from meet_assistant import HAS_AUDIO, diarizer
from meet_assistant.audio import find_monitor_source
from meet_assistant.engines import AVAILABLE_ENGINES, ENGINE_CLASSES
from meet_assistant.server import app


def main():
    parser = argparse.ArgumentParser(prog="p3x-meet-assistant",
                                     description="Meet Assistant Web GUI")
    parser.add_argument("--port", type=int, default=8088, help="Web server port (default: 8088)")
    parser.add_argument("--host", default="0.0.0.0", help="Web server host (default: 0.0.0.0)")
    parser.add_argument("--device", type=int, default=11,
                        help="PyAudio device index for speaker monitor (default: 11)")
    parser.add_argument("--dev", action="store_true", help="Dev mode: auto-reload Python on file changes")
    args = parser.parse_args()

    if "openai" not in AVAILABLE_ENGINES:
        print("Error: OpenAI API key not found.")
        print("  Set OPENAI_API_KEY in .env (see .env.example)")
        print("  OR export OPENAI_API_KEY=... in your shell")
        print("  Get a key: https://platform.openai.com/api-keys")
        sys.exit(1)

    print(f"\n  Loading engine: {AVAILABLE_ENGINES['openai']}...")
    state.current_engine = ENGINE_CLASSES["openai"]()
    state.current_engine_name = "openai"
    print("  Engine ready!")

    if diarizer.is_available():
        print(f"  Diarizer ready on {diarizer.device()}")
    else:
        print("  Diarizer unavailable - transcripts will not have speaker labels")
        print("  Install with: pip install resemblyzer")

    capture_mode = "browser"
    if HAS_AUDIO:
        from meet_assistant.audio import _suppress_stderr, _restore_stderr
        import speech_recognition as sr

        monitor = find_monitor_source()
        if monitor:
            capture_mode = "server"
            print(f"  Speaker source: {monitor}")
            os.environ["PULSE_SOURCE"] = monitor

            old_err = _suppress_stderr()
            recognizer = sr.Recognizer()
            recognizer.pause_threshold = 2.0
            recognizer.non_speaking_duration = 1.0
            speaker = sr.Microphone(device_index=args.device)
            _restore_stderr(old_err)

            state.server_capture = True
            threading.Thread(target=state.speaker_capture_loop,
                             args=(recognizer, speaker), daemon=True).start()

    if capture_mode == "browser":
        print("  No PulseAudio - browser capture mode (use MIC/TAB buttons)")

    print(f"\n  {'=' * 50}")
    print(f"  Meet Assistant Web")
    print(f"  http://localhost:{args.port}")
    print(f"  Capture: {capture_mode}")
    if args.dev:
        print(f"  Dev mode: auto-reload ON")
    print(f"  {'=' * 50}\n")

    if args.dev:
        pkg_dir = os.path.dirname(os.path.abspath(__file__))
        uvicorn.run("meet_assistant.server:app", host=args.host, port=args.port,
                    reload=True, reload_dirs=[pkg_dir])
    else:
        uvicorn.run(app, host=args.host, port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
