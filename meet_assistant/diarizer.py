"""Speaker diarization via voice fingerprinting.

Computes a 256-dim embedding per audio chunk (resemblyzer / GE2E), then assigns
a stable `Speaker N` label by cosine-similarity against running cluster centroids.
Runs on GPU (CUDA) when available, falls back to CPU.
"""

import io
import threading
import wave as wavmod

try:
    import numpy as np
    _HAS_NUMPY = True
except ImportError:
    np = None
    _HAS_NUMPY = False

_encoder = None
_encoder_device = None
_encoder_lock = threading.Lock()

# Running speaker clusters: list of dicts { "centroid": np.ndarray, "count": int }
_clusters = []
_clusters_lock = threading.Lock()

# Cosine similarity threshold for matching an existing speaker.
# Higher = stricter (more new speakers), lower = looser (more merging).
# 0.75 is a reasonable default for resemblyzer / VoxCeleb embeddings.
SIMILARITY_THRESHOLD = 0.75


def _load_encoder():
    """Lazy-load the resemblyzer VoiceEncoder on CUDA if possible, else CPU."""
    global _encoder, _encoder_device
    if _encoder is not None:
        return _encoder
    with _encoder_lock:
        if _encoder is not None:
            return _encoder
        if not _HAS_NUMPY:
            print("  Diarizer: disabled (install with: pip install p3x-meet-assistant[gpu])")
            _encoder = False
            return _encoder
        try:
            import torch
            from resemblyzer import VoiceEncoder
            device = "cuda" if torch.cuda.is_available() else "cpu"
            _encoder = VoiceEncoder(device=device)
            _encoder_device = device
            print(f"  Diarizer: VoiceEncoder loaded on {device}")
        except Exception as e:
            print(f"  Diarizer: disabled ({e})")
            _encoder = False  # sentinel: unavailable
    return _encoder


def is_available():
    enc = _load_encoder()
    return enc is not None and enc is not False


def device():
    _load_encoder()
    return _encoder_device


def _wav_bytes_to_float32(wav_bytes):
    """Decode WAV bytes to mono float32 at 16kHz expected by resemblyzer."""
    with wavmod.open(io.BytesIO(wav_bytes), "rb") as wf:
        sample_rate = wf.getframerate()
        n_channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        frames = wf.readframes(wf.getnframes())
    if sample_width != 2:
        return None, None
    audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
    if n_channels > 1:
        audio = audio.reshape(-1, n_channels).mean(axis=1)
    return audio, sample_rate


def _resample_to_16k(audio, sample_rate):
    if sample_rate == 16000:
        return audio
    # Linear resample — good enough for voice embedding
    ratio = 16000 / sample_rate
    new_len = int(len(audio) * ratio)
    idx = np.linspace(0, len(audio) - 1, new_len)
    return np.interp(idx, np.arange(len(audio)), audio).astype(np.float32)


def _cosine(a, b):
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def identify_speaker(wav_bytes):
    """Return a 1-based integer speaker id for the given WAV chunk, or None on failure."""
    enc = _load_encoder()
    if not enc:
        return None
    try:
        audio, sr = _wav_bytes_to_float32(wav_bytes)
        if audio is None or len(audio) < 16000 * 0.5:  # <0.5s
            return None
        audio = _resample_to_16k(audio, sr)
        embedding = enc.embed_utterance(audio)
    except Exception:
        return None

    with _clusters_lock:
        best_idx, best_sim = -1, -1.0
        all_sims = []
        for i, c in enumerate(_clusters):
            sim = _cosine(embedding, c["centroid"])
            all_sims.append(sim)
            if sim > best_sim:
                best_sim, best_idx = sim, i
        if best_idx >= 0 and best_sim >= SIMILARITY_THRESHOLD:
            c = _clusters[best_idx]
            n = c["count"]
            c["centroid"] = (c["centroid"] * n + embedding) / (n + 1)
            c["count"] = n + 1
            sims_str = ", ".join(f"{s:.2f}" for s in all_sims)
            print(f"  [diarize] match S{best_idx + 1} (sim={best_sim:.2f}; all=[{sims_str}])")
            return best_idx + 1
        _clusters.append({"centroid": embedding.astype(np.float32), "count": 1})
        sims_str = ", ".join(f"{s:.2f}" for s in all_sims) if all_sims else "none"
        print(f"  [diarize] NEW S{len(_clusters)} (best={best_sim:.2f}; all=[{sims_str}])")
        return len(_clusters)


def reset():
    """Clear all learned speakers (e.g. new session)."""
    with _clusters_lock:
        _clusters.clear()


def speaker_count():
    with _clusters_lock:
        return len(_clusters)
