"""
Simulated buzzer — synthesises piezo-style square-wave tones via pygame.mixer.

Square waves are used because a passive piezo buzzer driven by a PWM square
wave is exactly what the real HCW-KC1206 produces. Short fade-in/out ramps
(8 ms) prevent the audible click that comes from an abrupt waveform start.

pygame.mixer.pre_init() is called in __init__ so that when DebugDisplay later
calls pygame.init() the mixer picks up the correct sample rate automatically.
If the mixer is already running (e.g. unit tests), pre_init() is a no-op.
"""

import threading
import time

import numpy as np
import pygame.mixer
import pygame.sndarray

from .buzzer_base import BuzzerBase

SAMPLE_RATE = 22050   # Hz — standard low-latency rate, fine for square waves
VOLUME      = 0.35    # 0.0–1.0; piezo buzzers are loud, keep this modest


class SimBuzzer(BuzzerBase):
    """Plays buzzer tones through the computer's speakers using pygame.mixer."""

    def __init__(self, pin=None):   # pin ignored; accepted so HardwareManager can pass it
        pygame.mixer.pre_init(frequency=SAMPLE_RATE, size=-16, channels=1, buffer=512)
        self._stop_event = threading.Event()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def beep(self, freq: float, duration: float) -> None:
        self._ensure_init()
        pygame.sndarray.make_sound(self._square_wave(freq, duration)).play()

    def play_sequence(self, notes: list) -> None:
        self._stop_event.clear()
        threading.Thread(target=self._run_seq, args=(notes,), daemon=True).start()

    def stop(self) -> None:
        self._stop_event.set()
        if pygame.mixer.get_init():
            pygame.mixer.stop()

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _ensure_init(self) -> None:
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=1, buffer=512)

    def _square_wave(self, freq: float, duration: float) -> np.ndarray:
        """Return a (n_samples,) int16 square wave with short fade ramps."""
        n = max(1, int(SAMPLE_RATE * duration))
        t = np.arange(n, dtype=np.float32) / SAMPLE_RATE
        wave = np.sign(np.sin(2 * np.pi * freq * t)).astype(np.float32)

        fade = min(int(SAMPLE_RATE * 0.008), n // 4)   # 8 ms fade
        if fade > 0:
            wave[:fade]  *= np.linspace(0.0, 1.0, fade, dtype=np.float32)
            wave[-fade:] *= np.linspace(1.0, 0.0, fade, dtype=np.float32)

        return (wave * VOLUME * 32767).astype(np.int16)

    def _run_seq(self, notes: list) -> None:
        self._ensure_init()
        for freq, duration in notes:
            if self._stop_event.is_set():
                break
            if freq > 0:
                pygame.sndarray.make_sound(self._square_wave(freq, duration)).play()
            # Wait out the note duration (interruptible)
            deadline = time.monotonic() + duration
            while time.monotonic() < deadline:
                if self._stop_event.is_set():
                    break
                time.sleep(0.005)
