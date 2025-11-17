#!/usr/bin/env python3
"""
Countdown Audio Builder
-----------------------
Generate a spoken-number countdown with beeps, rest prompts, and precise timing.
Features:
  - gTTS with on-disk caching (so repeated runs are fast)
  - Retry logic for flaky TTS calls
  - Normalized loudness, short fades, mono + consistent sample rate
  - Sine-wave beeps (configurable frequency, duration, gain)
  - "Rest" prompts every N counts (configurable)
  - Lead-in prompt (optional)
  - Timeline .json with labeled cue times.0 (ms) for editors / apps
  - Stream-safe assembly (build in WAV then export to MP3 once)
  - NEW: --skip-first-rest N to skip the first N rest periods
  - NEW: --mode minutes for time-based countdown (e.g., "30 minutes remaining")
  - NEW: --speak-interval N to speak only every N minutes
  - NEW: --speak-at to speak at specific minutes (e.g., "30,15,10,5,1")
"""

import argparse
import hashlib
import json
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from gtts import gTTS
from pydub import AudioSegment
from pydub.generators import Sine
from pydub.effects import normalize

# -----------------------------
# Helpers
# -----------------------------

TARGET_RATE = 44100

def prep(seg: AudioSegment, fade_ms: int = 12) -> AudioSegment:
    """Normalize, fade edges, and unify format (mono, sample rate)."""
    return (
        normalize(seg)
        .fade_in(fade_ms)
        .fade_out(fade_ms)
        .set_channels(1)
        .set_frame_rate(TARGET_RATE)
    )

def make_beep(freq_hz: int, ms: int, gain_db: float) -> AudioSegment:
    return prep(Sine(freq_hz).to_audio_segment(duration=ms).apply_gain(gain_db))

def tts_to_file(text: str, path: Path, lang: str = "en", tld: str = "com") -> None:
    gTTS(text=text, lang=lang, tld=tld).save(str(path))

def tts_with_retry_to_audiosegment(
    text: str, tmpdir: Path, lang: str = "en", tld: str = "com",
    retries: int = 3, delay: float = 1.2
) -> AudioSegment:
    last_err = None
    out_mp3 = tmpdir / "tts_tmp.mp3"
    for attempt in range(retries):
        try:
            tts_to_file(text, out_mp3, lang=lang, tld=tld)
            return AudioSegment.from_mp3(str(out_mp3))
        except Exception as e:
            last_err = e
            if attempt < retries - 1:
                time.sleep(delay * (attempt + 1))
    raise RuntimeError(f"TTS failed for '{text}': {last_err}")

def tts_cached(
    text: str, cache_dir: Path, tmpdir: Path, lang: str = "en", tld: str = "com",
    retries: int = 3, delay: float = 1.2
) -> AudioSegment:
    key = hashlib.md5(f"{lang}|{tld}|{text}".encode("utf-8")).hexdigest()
    mp3_path = cache_dir / f"{key}.mp3"
    if not mp3_path.exists():
        seg = tts_with_retry_to_audiosegment(text, tmpdir, lang, tld, retries, delay)
        seg.export(str(mp3_path), format="mp3")
    return AudioSegment.from_mp3(str(mp3_path))

@dataclass
class Settings:
    start: int
    interval: float
    long_interval: float
    every_n: int
    lang: str
    tld: str
    beep_freq: int
    beep_ms: int
    beep_gain: float
    fade_ms: int
    outfile: Path
    out_bitrate: str
    lead_in: Optional[str]
    lead_in_gap_ms: int
    rest_text: str
    skip_first_rest: int
    end_with: Optional[str]
    mode: str  # "numbers" or "minutes"
    speak_interval: int  # Speak every N minutes (0 = all)
    speak_at: Optional[List[int]]  # Speak at specific minutes
    minute_text: str  # Text to append (e.g., "minutes remaining")

# -----------------------------
# Assembly
# -----------------------------

def should_speak_minute(minute: int, settings: Settings) -> bool:
    """Determine if a minute should be spoken based on settings."""
    if settings.speak_at:
        return minute in settings.speak_at
    elif settings.speak_interval > 0:
        return minute % settings.speak_interval == 0 or minute == 1
    else:
        return True  # Speak all minutes

def build_minutes_countdown(settings: Settings, cache_dir: Path) -> Tuple[AudioSegment, List[dict]]:
    """Build a minutes-based countdown (e.g., '30 minutes remaining')."""
    cache_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as td:
        tmpdir = Path(td)

        # Precompute assets
        rest_seg = prep(tts_cached(settings.rest_text, cache_dir, tmpdir, settings.lang, settings.tld), settings.fade_ms) if settings.every_n > 0 else None
        beep = make_beep(settings.beep_freq, settings.beep_ms, settings.beep_gain)

        timeline = []
        t_ms = 0
        skipped_rests = 0

        combined = AudioSegment.silent(duration=0, frame_rate=TARGET_RATE)

        # Lead-in
        if settings.lead_in:
            lead = prep(tts_cached(settings.lead_in, cache_dir, tmpdir, settings.lang, settings.tld), settings.fade_ms)
            combined += lead
            timeline.append({"label": settings.lead_in, "start": t_ms, "end": t_ms + len(lead)})
            t_ms += len(lead)
            if settings.lead_in_gap_ms > 0:
                combined += AudioSegment.silent(duration=settings.lead_in_gap_ms)
                timeline.append({"label": "lead_gap", "start": t_ms, "end": t_ms + settings.lead_in_gap_ms})
                t_ms += settings.lead_in_gap_ms

        # Main countdown loop - minutes
        for i in range(settings.start, 0, -1):
            # Determine if we should speak this minute
            if should_speak_minute(i, settings):
                # Build the spoken text
                if i == 1:
                    text = f"1 {settings.minute_text.replace('minutes', 'minute')}" if 'minutes' in settings.minute_text else f"1 {settings.minute_text}"
                else:
                    text = f"{i} {settings.minute_text}"

                spoken = prep(tts_cached(text, cache_dir, tmpdir, settings.lang, settings.tld), settings.fade_ms)
                combined += spoken
                timeline.append({"label": text, "start": t_ms, "end": t_ms + len(spoken)})
                t_ms += len(spoken)

            if i == 1:
                # After final minute
                if settings.end_with:
                    end_seg = prep(
                        tts_cached(settings.end_with, cache_dir, tmpdir, settings.lang, settings.tld),
                        settings.fade_ms
                    )
                    combined += end_seg
                    timeline.append({
                        "label": settings.end_with,
                        "start": t_ms,
                        "end": t_ms + len(end_seg)
                    })
                    t_ms += len(end_seg)
                break

            # Determine rest vs normal interval
            if settings.every_n > 0 and (i % settings.every_n == 0):
                if skipped_rests < settings.skip_first_rest:
                    skipped_rests += 1
                    # Normal interval
                    combined += beep
                    timeline.append({"label": "beep_skip_rest", "start": t_ms, "end": t_ms + len(beep)})
                    t_ms += len(beep)

                    # 1 minute of silence (or interval time)
                    gap_ms = int(60000 if should_speak_minute(i, settings) else settings.interval * 1000)
                    combined += AudioSegment.silent(duration=gap_ms)
                    timeline.append({"label": "pause_skip_rest", "start": t_ms, "end": t_ms + gap_ms})
                    t_ms += gap_ms
                else:
                    # Rest cue
                    if rest_seg:
                        combined += rest_seg
                        timeline.append({"label": settings.rest_text, "start": t_ms, "end": t_ms + len(rest_seg)})
                        t_ms += len(rest_seg)

                    combined += beep
                    timeline.append({"label": "beep", "start": t_ms, "end": t_ms + len(beep)})
                    t_ms += len(beep)

                    gap_ms = int(settings.long_interval * 1000)
                    combined += AudioSegment.silent(duration=gap_ms)
                    timeline.append({"label": "pause_long", "start": t_ms, "end": t_ms + gap_ms})
                    t_ms += gap_ms
            else:
                # Normal interval - full minute of silence if spoken, else short interval
                combined += beep
                timeline.append({"label": "beep", "start": t_ms, "end": t_ms + len(beep)})
                t_ms += len(beep)

                gap_ms = int(60000 if should_speak_minute(i, settings) else settings.interval * 1000)
                combined += AudioSegment.silent(duration=gap_ms)
                timeline.append({"label": "pause", "start": t_ms, "end": t_ms + gap_ms})
                t_ms += gap_ms

        return combined, timeline

def build_countdown_audio(settings: Settings, cache_dir: Path) -> Tuple[AudioSegment, List[dict]]:
    cache_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as td:
        tmpdir = Path(td)

        # Precompute assets
        rest_seg = prep(tts_cached(settings.rest_text, cache_dir, tmpdir, settings.lang, settings.tld), settings.fade_ms)
        beep = make_beep(settings.beep_freq, settings.beep_ms, settings.beep_gain)

        timeline = []
        t_ms = 0
        skipped_rests = 0  # NEW

        combined = AudioSegment.silent(duration=0, frame_rate=TARGET_RATE)

        # Lead-in
        if settings.lead_in:
            lead = prep(tts_cached(settings.lead_in, cache_dir, tmpdir, settings.lang, settings.tld), settings.fade_ms)
            combined += lead
            timeline.append({"label": settings.lead_in, "start": t_ms, "end": t_ms + len(lead)})
            t_ms += len(lead)
            if settings.lead_in_gap_ms > 0:
                combined += AudioSegment.silent(duration=settings.lead_in_gap_ms)
                timeline.append({"label": "lead_gap", "start": t_ms, "end": t_ms + settings.lead_in_gap_ms})
                t_ms += settings.lead_in_gap_ms

                # Main loop
        for i in range(settings.start, 0, -1):
            spoken = prep(tts_cached(str(i), cache_dir, tmpdir, settings.lang, settings.tld), settings.fade_ms)
            combined += spoken
            timeline.append({"label": str(i), "start": t_ms, "end": t_ms + len(spoken)})
            t_ms += len(spoken)

            if i == 1:
                # After final "1"
                if settings.end_with:
                    end_seg = prep(
                        tts_cached(settings.end_with, cache_dir, tmpdir, settings.lang, settings.tld),
                        settings.fade_ms
                    )
                    combined += end_seg
                    timeline.append({
                        "label": settings.end_with,
                        "start": t_ms,
                        "end": t_ms + len(end_seg)
                    })
                    t_ms += len(end_seg)
                break


            # Determine rest vs normal
            if settings.every_n > 0 and (i % settings.every_n == 0):
                if skipped_rests < settings.skip_first_rest:
                    skipped_rests += 1
                    # behave like normal interval
                    combined += beep
                    timeline.append({"label": "beep_skip_rest", "start": t_ms, "end": t_ms + len(beep)})
                    t_ms += len(beep)

                    gap_ms = int(settings.interval * 1000)
                    combined += AudioSegment.silent(duration=gap_ms)
                    timeline.append({"label": "pause_skip_rest", "start": t_ms, "end": t_ms + gap_ms})
                    t_ms += gap_ms
                else:
                    # Normal rest cue
                    combined += rest_seg
                    timeline.append({"label": settings.rest_text, "start": t_ms, "end": t_ms + len(rest_seg)})
                    t_ms += len(rest_seg)

                    combined += beep
                    timeline.append({"label": "beep", "start": t_ms, "end": t_ms + len(beep)})
                    t_ms += len(beep)

                    gap_ms = int(settings.long_interval * 1000)
                    combined += AudioSegment.silent(duration=gap_ms)
                    timeline.append({"label": "pause_long", "start": t_ms, "end": t_ms + gap_ms})
                    t_ms += gap_ms
            else:
                # normal step
                combined += beep
                timeline.append({"label": "beep", "start": t_ms, "end": t_ms + len(beep)})
                t_ms += len(beep)

                gap_ms = int(settings.interval * 1000)
                combined += AudioSegment.silent(duration=gap_ms)
                timeline.append({"label": "pause", "start": t_ms, "end": t_ms + gap_ms})
                t_ms += gap_ms
                
                

        return combined, timeline

# -----------------------------
# CLI
# -----------------------------

def parse_args(argv: Optional[List[str]] = None) -> Settings:
    p = argparse.ArgumentParser(description="Build a voiced countdown with beeps and rest prompts.")
    p.add_argument("--start", type=int, default=80, help="Starting number for countdown (reps or minutes depending on mode).")
    p.add_argument("--mode", choices=["numbers", "minutes"], default="numbers", help="Countdown mode: 'numbers' (default) or 'minutes'.")
    p.add_argument("--interval", type=float, default=3.5, help="Seconds between normal cues (for numbers mode or silent minutes).")
    p.add_argument("--long-interval", type=float, default=8.0, help="Seconds after a rest cue.")
    p.add_argument("--every-n", type=int, default=8, help="Insert 'rest' every N counts. Use 0 to disable.")
    p.add_argument("--speak-interval", type=int, default=0, help="(Minutes mode) Speak every N minutes. 0 = all minutes.")
    p.add_argument("--speak-at", default=None, help="(Minutes mode) Speak only at specific minutes (comma-separated, e.g., '30,15,10,5,1').")
    p.add_argument("--minute-text", default="minutes remaining", help="(Minutes mode) Text to append to minute count.")
    p.add_argument("--lang", default="en", help="gTTS language code (e.g., en, es).")
    p.add_argument("--tld", default="com", help="gTTS voice region (com, co.uk, com.au, etc.).")
    p.add_argument("--beep-freq", type=int, default=1000, help="Beep frequency in Hz.")
    p.add_argument("--beep-ms", type=int, default=300, help="Beep duration in ms.")
    p.add_argument("--beep-gain", type=float, default=-6.0, help="Beep gain in dB (negative = quieter).")
    p.add_argument("--fade-ms", type=int, default=12, help="Fade in/out per segment to avoid clicks.")
    p.add_argument("--outfile", default="countdown_combined.mp3", help="Output MP3 file path.")
    p.add_argument("--out-bitrate", default="192k", help="MP3 bitrate, e.g. 128k, 192k, 256k.")
    p.add_argument("--lead-in", default=None, help="Optional spoken lead-in line (e.g., 'Get ready').")
    p.add_argument("--lead-in-gap-ms", type=int, default=1000, help="Silence after lead-in (ms).")
    p.add_argument("--rest-text", default="rest", help="Word to speak at rest cues.")
    p.add_argument("--skip-first-rest", type=int, default=0, help="Number of initial rest periods to skip.")
    p.add_argument("--end-with", default=None, help="Optional spoken phrase to play at the very end (e.g., 'Good Job!').")

    args = p.parse_args(argv)

    # Parse speak_at if provided
    speak_at_list = None
    if args.speak_at:
        try:
            speak_at_list = [int(x.strip()) for x in args.speak_at.split(',')]
        except ValueError:
            raise ValueError("--speak-at must be comma-separated integers (e.g., '30,15,10,5,1')")

    return Settings(
        start=args.start,
        interval=args.interval,
        long_interval=args.long_interval,
        every_n=args.every_n,
        lang=args.lang,
        tld=args.tld,
        beep_freq=args.beep_freq,
        beep_ms=args.beep_ms,
        beep_gain=args.beep_gain,
        fade_ms=args.fade_ms,
        outfile=Path(args.outfile),
        out_bitrate=args.out_bitrate,
        lead_in=args.lead_in,
        lead_in_gap_ms=args.lead_in_gap_ms,
        rest_text=args.rest_text,
        skip_first_rest=args.skip_first_rest,
        end_with=args.end_with,
        mode=args.mode,
        speak_interval=args.speak_interval,
        speak_at=speak_at_list,
        minute_text=args.minute_text
    )

def main(argv: Optional[List[str]] = None) -> int:
    settings = parse_args(argv)

    try:
        _ = AudioSegment.silent(duration=10, frame_rate=TARGET_RATE)
    except Exception as e:
        print("pydub/ffmpeg not ready: ", e, file=sys.stderr)
        return 2

    cache_dir = Path("tts_cache")
    cache_dir.mkdir(exist_ok=True, parents=True)

    # Choose builder based on mode
    if settings.mode == "minutes":
        print(f"Building {settings.start}-minute countdown...")
        audio, timeline = build_minutes_countdown(settings, cache_dir)
    else:
        print(f"Building {settings.start}-count countdown...")
        audio, timeline = build_countdown_audio(settings, cache_dir)

    # Export WAV then MP3 once
    with tempfile.TemporaryDirectory() as td:
        tmp_wav = Path(td) / "combined.wav"
        audio.export(str(tmp_wav), format="wav")
        final = AudioSegment.from_wav(str(tmp_wav))
        settings.outfile.parent.mkdir(parents=True, exist_ok=True)
        final.export(str(settings.outfile), format="mp3", bitrate=settings.out_bitrate)

    # Save timeline JSON
    timeline_path = settings.outfile.with_suffix(".json")
    with open(timeline_path, "w", encoding="utf-8") as f:
        json.dump(timeline, f, indent=2)

    print(f"Wrote: {settings.outfile}")
    print(f"Wrote: {timeline_path}")
    print("Tip: caches in ./tts_cache (delete to refresh voices).")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

