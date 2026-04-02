"""
Abstract buzzer interface.

Subclasses:
    SimBuzzer  — synthesises square-wave tones through pygame.mixer (dev)
    RealBuzzer — drives the HCW-KC1206 passive piezo via BeagleBone PWM
"""

from abc import ABC, abstractmethod


class BuzzerBase(ABC):
    """
    Public API:
        beep(freq, duration)          — play one tone, non-blocking
        play_sequence(notes)          — play [(freq, duration), ...], non-blocking
                                        freq=0 is a rest (silence)
        stop()                        — interrupt any playing sound immediately
    """

    @abstractmethod
    def beep(self, freq: float, duration: float) -> None:
        """Play a single square-wave tone. Returns immediately."""

    @abstractmethod
    def play_sequence(self, notes: list) -> None:
        """
        Play a sequence of notes on a background thread. Returns immediately.

        Args:
            notes: list of (freq_hz, duration_s). freq=0 inserts a silent rest.
        """

    @abstractmethod
    def stop(self) -> None:
        """Stop all sound immediately and cancel any running sequence."""
