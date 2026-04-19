[//]: #@corifeus-header

  [![Donate for PatrikX3 / P3X](https://img.shields.io/badge/Donate-PatrikX3-003087.svg)](https://paypal.me/patrikx3) [![Contact Corifeus / P3X](https://img.shields.io/badge/Contact-P3X-ff9900.svg)](https://www.patrikx3.com/en/front/contact) [![Corifeus @ Facebook](https://img.shields.io/badge/Facebook-Corifeus-3b5998.svg)](https://www.facebook.com/corifeus.software)  [![Uptime ratio (90 days)](https://network.corifeus.com/public/api/uptime-shield/31ad7a5c194347c33e5445dbaf8.svg)](https://network.corifeus.com/status/31ad7a5c194347c33e5445dbaf8)





# 🎙️🧠 Real-time AI speech-to-text for meetings with GPT-4o Transcribe and GPU speaker diarization v2026.4.120


  
🌌 **Bugs are evident™ - MATRIX️**  
🚧 **This project is under active development!**  
📢 **We welcome your feedback and contributions.**  
    



### NodeJS LTS is supported

### 🛠️ Built on NodeJs version

```txt
v24.14.1
```





# 📝 Description

                        
[//]: #@corifeus-header:end
# Meet Assistant

Real-time AI speech-to-text for meetings and conversations. Captures speaker audio, transcribes it live using **OpenAI GPT-4o Transcribe**, and auto-labels each utterance by voice (Speaker 1, Speaker 2, ...). Supports 10 European languages out of the box.

[![PyPI](https://img.shields.io/pypi/v/p3x-meet-assistant.svg?label=PyPI)](https://pypi.org/project/p3x-meet-assistant/)
[![Python](https://img.shields.io/pypi/pyversions/p3x-meet-assistant.svg)](https://pypi.org/project/p3x-meet-assistant/)
[![Downloads](https://img.shields.io/pypi/dm/p3x-meet-assistant.svg)](https://pypi.org/project/p3x-meet-assistant/)
![engine](https://img.shields.io/badge/engine-GPT--4o%20Transcribe-blue)
![diarization](https://img.shields.io/badge/speaker%20diarization-GPU-orange)
![license](https://img.shields.io/badge/license-MIT-green)

## Links

- **PyPI package**: <https://pypi.org/project/p3x-meet-assistant/>
- **GitHub repository**: <https://github.com/patrikx3/meet-assistant>
- **Releases & changelogs**: <https://github.com/patrikx3/meet-assistant/releases>
- **Issue tracker**: <https://github.com/patrikx3/meet-assistant/issues>
- **Homepage**: <https://corifeus.com/meet-assistant>

## Quickstart — install from PyPI

```bash
pip install p3x-meet-assistant
export OPENAI_API_KEY=sk-...
p3x-meet-assistant
```

Open <http://localhost:8088>. That's the whole thing.

The bundled wheel ships the full web UI — no Node.js, no `git clone`, no build step needed at runtime.

Package on PyPI: <https://pypi.org/project/p3x-meet-assistant/>

## What you get

- Live transcription via **OpenAI GPT-4o Transcribe** — the highest-accuracy speech model available today
- Auto speaker diarization — colored `Speaker 1 / 2 / 3 ...` labels based on voice fingerprint
- 10 languages: **English, Hungarian, German, French, Spanish, Italian, Portuguese, Dutch, Polish, Czech**
- Browser-based UI — Dark / Light theme, adjustable font size, one-click transcript export
- Captures system audio on Linux (PulseAudio / PipeWire) or any audio in a browser tab via MIC / TAB buttons
- Distributed as a **pip-installable Python package** — [`p3x-meet-assistant` on PyPI](https://pypi.org/project/p3x-meet-assistant/)

## Why one language at a time?

Auto-detect mode (trying two languages and picking the best) produces far more hallucinations than explicitly selecting a single language. Pick the language you're actually hearing, and accuracy jumps dramatically.

## Platforms — works on Linux, macOS, and Windows

Meet Assistant runs on **any OS with Python 3.10+ and a modern browser**. The only feature that's Linux-specific is the optional server-side system-audio capture. Everywhere else you use the browser's built-in audio capture — same APIs Google Meet uses.

| Platform | Install | Microphone | System / tab audio | GPU diarization |
| :--- | :--- | :--- | :--- | :--- |
| **Linux** (desktop) | `pip install 'p3x-meet-assistant[linux-capture]'` + `sudo apt install portaudio19-dev` | ✓ **MIC** button | ✓ Auto-captured via PulseAudio / PipeWire (plus **TAB** button) | ✓ NVIDIA CUDA |
| **macOS** | `pip install p3x-meet-assistant` | ✓ **MIC** button | ✓ **TAB** button (Chrome/Edge; share a tab with audio) | ✓ CPU or Apple Silicon eGPU |
| **Windows** | `pip install p3x-meet-assistant` | ✓ **MIC** button | ✓ **TAB** button | ✓ NVIDIA CUDA or CPU |
| **Cloud server** | `pip install p3x-meet-assistant` | — (no local audio) | Browser capture from the user's machine | Optional CPU diarization |

### macOS specifics

- The standard `pip install p3x-meet-assistant` works. No homebrew needed for the default setup.
- For meetings in Google Meet / Zoom / Teams, use the **TAB** button in the browser — it works identically to how you'd share audio in a Meet call.
- To capture system audio *outside* a browser tab (e.g. a desktop Zoom app), install [BlackHole](https://github.com/ExistentialAudio/BlackHole) or Loopback to create a virtual audio device, then select it as the browser's microphone input.
- For GPU speaker diarization on Apple Silicon, the `[gpu]` extra installs `torch`; it runs on the Metal backend automatically.

### Windows specifics

- The standard `pip install p3x-meet-assistant` works on Windows 10/11.
- Open **PowerShell** or **Command Prompt** and run `p3x-meet-assistant`.
- **TAB** button captures any browser-tab audio (the same permission flow as Meet's "Share a tab" with the "Share audio" checkbox).
- If you want system-wide capture, tools like VB-Audio Cable or Voicemeeter expose a virtual microphone that routes all system audio into the browser.
- NVIDIA GPU diarization works out of the box via the `[gpu]` extra.

### Requirements — bare minimum

- Python 3.10+
- A modern browser (Chrome, Firefox, Edge)
- An OpenAI API key

Node.js is **not** required when installing from PyPI — the wheel ships the pre-built frontend.

### Requirements — optional extras

- **Linux system-audio capture**: `portaudio19-dev` package + the `[linux-capture]` pip extra
- **Speaker diarization**: any NVIDIA GPU with ~500 MB VRAM (GTX 1650 / RTX 2060 and up) + the `[gpu]` pip extra. CPU fallback works but is slower.

No GPU is fine — the app degrades gracefully. You lose speaker labels but everything else works.

## Install from PyPI

The recommended path for anyone who just wants to **use** Meet Assistant. The Python wheel bundles the pre-built frontend, so there's no Node.js, no build step, no `git clone` — just `pip install` and go.

### 1. One-time setup — create a virtual environment

Skip straight to step 2 if you already use a venv or a managed environment like `pipx`, `poetry`, or `uv`.

```bash
python3 -m venv ~/.venvs/meet-assistant
source ~/.venvs/meet-assistant/bin/activate
```

Installing into the system Python works too, but a venv keeps dependencies isolated. On some modern Linux distros (Ubuntu 24.04+, Debian 12+) system-wide `pip install` is blocked by PEP 668 — a venv (or `pipx`) is required.

### 2. Install the package

Pick the variant that matches your hardware. All four commands install the same core package; the optional extras pull in additional wheels for features you want.

| Command | What you get | Wheel size | Recommended for |
| :--- | :--- | :--- | :--- |
| `pip install p3x-meet-assistant` | Cloud transcription (GPT-4o) + browser audio capture | ~300 kB + deps (~40 MB) | Laptops, macOS/Windows, cloud servers |
| `pip install 'p3x-meet-assistant[gpu]'` | Above + GPU speaker diarization (`resemblyzer` + `torch`) | ~700 MB total | Workstations with any NVIDIA GPU |
| `pip install 'p3x-meet-assistant[linux-capture]'` | Above + server-side PulseAudio / PipeWire capture (`SpeechRecognition` + `PyAudio`) | ~40 MB + system portaudio | Linux desktops that want system-audio capture |
| `pip install 'p3x-meet-assistant[all]'` | Everything together | ~700 MB | Full local workstation install |

Linux users with `[linux-capture]` or `[all]` need the PortAudio dev headers before `pip install`:

```bash
sudo apt install portaudio19-dev
```

### 3. Provide your OpenAI API key

Get a key at <https://platform.openai.com/api-keys>, then either:

**Option A — environment variable** (quickest):

```bash
export OPENAI_API_KEY=sk-...
```

Add it to `~/.bashrc` / `~/.zshrc` if you want it permanent.

**Option B — `.env` file in your working directory**:

```bash
cd ~/my-meetings                  # wherever you run the command from
echo "OPENAI_API_KEY=sk-..." > .env
```

Meet Assistant automatically loads `.env` from the current working directory on startup.

### 4. Run it

```bash
p3x-meet-assistant
```

Open <http://localhost:8088> in your browser. Pick a language from the top dropdown, then either:

- Click **MIC** to transcribe your microphone
- Click **TAB** to share a browser tab with audio (Google Meet, YouTube, a Facebook stream — anything with "Share audio" enabled)
- On Linux with `[linux-capture]` installed, the server auto-detects the system speaker monitor and starts transcribing immediately

Every transcript is appended to `sessions/YYYY-MM-DD-HH-MM.txt` in your working directory automatically.

### Upgrade or uninstall

```bash
pip install --upgrade p3x-meet-assistant            # latest stable
pip install 'p3x-meet-assistant==2026.4.109'        # pin to a specific release
pip uninstall p3x-meet-assistant                    # remove
```

Release notes for every version: <https://github.com/patrikx3/meet-assistant/releases>.

### What gets installed

The wheel contains:

- `meet_assistant/` — the Python package (FastAPI server, OpenAI client, diarizer, state manager)
- `meet_assistant/dist/` — the pre-built Vite frontend (HTML, JS, CSS, Font Awesome fonts)
- Entry point `p3x-meet-assistant` → `meet_assistant.cli:main`

What's **not** in the wheel (excluded by `MANIFEST.in`): `secure/`, `agents/`, `.claude/`, `.vscode/`, `AGENTS.md`, `CLAUDE.md`, source-only configs, the dev launcher, and any tokens. Safe to install from PyPI.

### Troubleshooting a pip install

| Symptom | Fix |
| :--- | :--- |
| `externally-managed-environment` (PEP 668) | Use a venv (`python3 -m venv`) or `pipx install p3x-meet-assistant` |
| `Could not build wheels for PyAudio` on Linux | Install `portaudio19-dev`: `sudo apt install portaudio19-dev` |
| `Could not build wheels for PyAudio` on macOS | `brew install portaudio` then retry |
| `No module named 'torch'` at runtime | Install the `[gpu]` extra or skip diarization |
| Port 8088 already in use | Run with `p3x-meet-assistant --port 9000` (or any free port) |
| `No OpenAI API key found` | Set `OPENAI_API_KEY` in your shell or `.env` in the working directory |

## Install from source (development workflow)

Only needed if you want to hack on the code itself.

```bash
git clone https://github.com/patrikx3/meet-assistant.git
cd meet-assistant

# Linux only — for PulseAudio capture
sudo apt install portaudio19-dev

# Python venv
python3 -m venv venv

# Pick ONE based on your hardware:
./venv/bin/pip install -r requirements.txt        # full local with GPU
./venv/bin/pip install -r requirements-cloud.txt  # cloud-only, no GPU

# Frontend build
yarn install
yarn build:web

# Dev launcher (auto-reload)
./meet-assistant-web.py --dev
```

Want diarization later on an already-installed source checkout? Just add:

```bash
./venv/bin/pip install resemblyzer
```

## API key

You need **one** OpenAI API key. Get it at <https://platform.openai.com/api-keys>.

### Option A — `.env` file (recommended)

```bash
cp .env.example .env
# Edit .env and paste your key:  OPENAI_API_KEY=sk-...
```

The `.env` file is gitignored and auto-loaded on startup.

### Option B — shell environment variable

```bash
export OPENAI_API_KEY=sk-...
./meet-assistant-web.py
```

For a permanent setup, add the `export` line to `~/.bashrc` or `~/.zshrc`.

## Run

```bash
./meet-assistant-web.py
```

Open <http://localhost:8088> in your browser. Pick a language from the dropdown, start talking (or open a Google Meet), watch the transcript flow in.

### Command-line options

| Flag | Default | Description |
| :--- | :--- | :--- |
| `--port PORT` | `8088` | Web server port |
| `--host HOST` | `0.0.0.0` | Web server host |
| `--dev` | off | Auto-reload on Python file changes |
| `--device INDEX` | `11` | PyAudio device index for the speaker monitor (Linux only) |

## Speaker diarization

If the diarizer loaded successfully (check the startup console output), every transcribed line is prefixed with a `Speaker N` label, color-coded in the UI. Clusters live in memory for the session — click the **Clear** button to wipe them and start fresh.

- Runs on GPU (CUDA) automatically, falls back to CPU if no GPU is available
- Adds ~20 ms per chunk on a modern NVIDIA card — imperceptible
- Language-independent (voice fingerprint, not words)
- Tuning knob: `SIMILARITY_THRESHOLD` in [web/diarizer.py](web/diarizer.py). Lower = more merging, higher = more splitting. Default: `0.75`.

**Troubleshooting the clustering:**

- Same person gets split across multiple speakers → lower the threshold to ~0.65
- Different people collapse into one speaker → raise the threshold to ~0.82

## Session auto-save

Every transcript is appended to `sessions/YYYY-MM-DD-HH-MM.txt` as it arrives — nothing to click. A new file is started each time you hit **Clear**, or each time you restart the server. The folder is gitignored by default.

## Rolling prompt context

Each transcription call passes the last ~400 characters of the session as its OpenAI `prompt` hint. This keeps proper nouns, jargon, and acronyms spelled consistently across chunks instead of being re-invented every 5 seconds. Costs nothing extra.

## How audio is captured

**Linux with PulseAudio / PipeWire (default on a local workstation):**
The app auto-detects your speakers' monitor source and records everything that plays on them — meeting audio, video calls, YouTube, Facebook streams, anything audible. No routing setup needed.

**Any OS (or cloud deployment):**
Click the **MIC** button to transcribe your microphone, or the **TAB** button to share a browser tab with audio (identical to Google Meet's "Share tab with audio" feature). Uses the standard `getUserMedia` / `getDisplayMedia` browser APIs.

## Use with Google Meet / Zoom / Teams / Facebook Live

Start Meet Assistant, then join your call or open your stream as normal. On Linux, system audio is captured automatically. On other platforms, click **TAB** and select the meeting tab with "Share audio" enabled.

## Development

```bash
# Frontend dev server with HMR (port 5173, proxies /ws to :8088)
npm run dev

# Production build
npm run build:web

# Backend with auto-reload on file changes
./meet-assistant-web.py --dev
```

**VS Code:** open the project and press **F5** — preset launch configs are wired up.

## Project structure

```
meet-assistant-web.py         # Entry point
web/
  __init__.py                 # Package init, .env auto-load, audio bootstrap
  audio.py                    # PulseAudio source detection
  engines.py                  # OpenAI GPT-4o Transcribe wrapper + hallucination filter
  diarizer.py                 # Speaker diarization (resemblyzer on CUDA)
  state.py                    # App state, WebSocket broadcast, capture loop
  server.py                   # FastAPI app, routes, WebSocket handler
  src/                        # Frontend source (Vite)
    index.html
    main.js
    style.css
  dist/                       # Built frontend (gitignored)
requirements.txt              # Full deps with GPU diarization
requirements-cloud.txt        # Lean deps, cloud-only (no diarization)
.env.example                  # Template for your API key
```

## Troubleshooting

| Symptom | Fix |
| :--- | :--- |
| `No OpenAI API key found` | Set `OPENAI_API_KEY` in `.env` or `export` it in your shell |
| `No monitor source found` | You're not on PulseAudio/PipeWire — use the **MIC** or **TAB** browser buttons |
| `Diarizer unavailable` | Install `resemblyzer`: `./venv/bin/pip install resemblyzer` — or ignore if you don't want speaker labels |
| One person tagged as multiple speakers | Lower `SIMILARITY_THRESHOLD` in `web/diarizer.py` to ~0.65 |
| Multiple people collapsed into one speaker | Raise `SIMILARITY_THRESHOLD` to ~0.82 |
| Too many hallucinations on silent audio | Already filtered — see `_is_hallucination` in `web/engines.py` |

## License

MIT

[//]: #@corifeus-footer

---

# Corifeus Network

AI-powered network & email toolkit — free, no signup.

**Web** · [network.corifeus.com](https://network.corifeus.com)  **MCP** · [`npm i -g p3x-network-mcp`](https://www.npmjs.com/package/p3x-network-mcp)

- **AI Network Assistant** — ask in plain language, get a full domain health report
- **Network Audit** — DNS, SSL, security headers, DNSBL, BGP, IPv6, geolocation in one call
- **Diagnostics** — DNS lookup & global propagation, WHOIS, reverse DNS, HTTP check, my-IP
- **Mail Tester** — live SPF/DKIM/DMARC + spam score + AI fix suggestions, results emailed (localized)
- **Monitoring** — TCP / HTTP / Ping with alerts and public status pages
- **MCP server** — 17 tools exposed to Claude Code, Codex, Cursor, any MCP client
- **Install** — `claude mcp add p3x-network -- npx p3x-network-mcp`
- **Try** — *"audit example.com"*, *"why do my emails land in spam? test me@example.com"*
- **Source** — [patrikx3/network](https://github.com/patrikx3/network) · [patrikx3/network-mcp](https://github.com/patrikx3/network-mcp)
- **Contact** — [patrikx3.com](https://www.patrikx3.com/en/front/contact) · [donate](https://paypal.me/patrikx3)

---

## ❤️ Support Our Open-Source Project  
If you appreciate our work, consider ⭐ starring this repository or 💰 making a donation to support server maintenance and ongoing development. Your support means the world to us—thank you!  

---

### 🌍 About My Domains  
All my domains, including [patrikx3.com](https://patrikx3.com), [corifeus.eu](https://corifeus.eu), and [corifeus.com](https://corifeus.com), are developed in my spare time. While you may encounter minor errors, the sites are generally stable and fully functional.  

---

### 📈 Versioning Policy  
**Version Structure:** We follow a **Major.Minor.Patch** versioning scheme:  
- **Major:** 📅 Corresponds to the current year.  
- **Minor:** 🌓 Set as 4 for releases from January to June, and 10 for July to December.  
- **Patch:** 🔧 Incremental, updated with each build.  

**🚨 Important Changes:** Any breaking changes are prominently noted in the readme to keep you informed.


[**P3X-MEET-ASSISTANT**](https://corifeus.com/meet-assistant) Build v2026.4.120

 [![Donate for PatrikX3 / P3X](https://img.shields.io/badge/Donate-PatrikX3-003087.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=QZVM4V6HVZJW6)  [![Contact Corifeus / P3X](https://img.shields.io/badge/Contact-P3X-ff9900.svg)](https://www.patrikx3.com/en/front/contact) [![Like Corifeus @ Facebook](https://img.shields.io/badge/LIKE-Corifeus-3b5998.svg)](https://www.facebook.com/corifeus.software)





[//]: #@corifeus-footer:end