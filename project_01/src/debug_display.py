"""
DebugDisplay — pygame "digital clone" of the 32x32 LED matrix.

Rendering approach:
    1. Build a core image: each LED is a bright filled circle (not a square block).
    2. Gaussian-blur the core to produce a soft glow layer.
    3. Composite: dark_bg + glow * GLOW_INTENSITY + core, clipped to [0, 255].

Because the glow layer is added (not alpha-blended), overlapping glows from
adjacent lit LEDs accumulate exactly like real light sources would.

Tuning constants (near the top of the file):
    SCALE             pixels per LED cell  (default 16 → 512×512 window)
    LED_RADIUS_FACTOR LED circle radius as a fraction of SCALE
    GLOW_SIGMA_FACTOR gaussian sigma as a fraction of SCALE
    GLOW_INTENSITY    brightness multiplier for the glow layer
    BG_COLOR          background RGB (very dark; shows as the LED panel body)

Keyboard mapping:
    A / D      → left / right button
    W / S      → select / back button
    ← / →      → virtual IMU yaw rotation (held)
    ↑ / ↓      → virtual IMU pitch rotation (held)
    Escape / Q → quit

Dependencies:
    pip install pygame numpy scipy
    (scipy is used for gaussian_filter; falls back to a box-blur approximation)
"""

import pygame
import numpy as np

try:
    from scipy.ndimage import gaussian_filter as _scipy_gblur
    _HAS_SCIPY = True
except ImportError:
    _HAS_SCIPY = False

# ---------------------------------------------------------------------------
# Tuning constants
# ---------------------------------------------------------------------------

SCALE             = 16      # pixels per LED  →  32 * 16 = 512 px window
FPS               = 60
ARROW_RATE        = 90.0    # deg/s injected while an arrow key is held

BG_COLOR          = np.array([6, 6, 10],  dtype=np.float32)  # near-black panel body
LED_RADIUS_FACTOR = 0.28    # LED dot radius as fraction of SCALE  (0.28 * 16 ≈ 4.5 px)
GLOW_SIGMA_FACTOR = 0.9     # gaussian sigma as fraction of SCALE
GLOW_INTENSITY    = 1.8     # how much brighter the glow layer is vs the raw blur

# ---------------------------------------------------------------------------
# Input key maps
# ---------------------------------------------------------------------------

_BUTTON_KEYS = {
    pygame.K_a: 'left',
    pygame.K_d: 'right',
    pygame.K_w: 'select',
    pygame.K_s: 'back',
}

_ARROW_KEYS = {
    pygame.K_LEFT:  ('yaw',   -ARROW_RATE),
    pygame.K_RIGHT: ('yaw',   +ARROW_RATE),
    pygame.K_UP:    ('pitch', +ARROW_RATE),
    pygame.K_DOWN:  ('pitch', -ARROW_RATE),
}

# ---------------------------------------------------------------------------
# Rendering helpers (module-level so they can be precomputed at import time)
# ---------------------------------------------------------------------------

def _build_led_mask(scale: int) -> np.ndarray:
    """Return a (scale, scale) float32 array: 1.0 inside the LED circle, 0.0 outside."""
    r  = scale * LED_RADIUS_FACTOR
    y, x = np.ogrid[:scale, :scale]
    cx = cy = scale / 2.0
    return ((x - cx) ** 2 + (y - cy) ** 2 <= r ** 2).astype(np.float32)


def _glow_blur(img: np.ndarray, sigma: float) -> np.ndarray:
    """
    Gaussian blur of a float32 (H, W, 3) image.
    Uses scipy.ndimage.gaussian_filter when available (fast, high quality).
    Falls back to a 3-pass box-blur approximation otherwise.
    """
    if _HAS_SCIPY:
        return _scipy_gblur(img, sigma=[sigma, sigma, 0])
    return _box_blur_approx(img, sigma)


def _box_blur_approx(img: np.ndarray, sigma: float) -> np.ndarray:
    """3-pass box blur — O(N) gaussian approximation via cumulative sums."""
    radius = max(1, int(sigma * 0.7))
    result = img.astype(np.float32)
    for _ in range(3):
        result = _box_blur_axis(result, radius, 0)
        result = _box_blur_axis(result, radius, 1)
    return result


def _box_blur_axis(arr: np.ndarray, radius: int, axis: int) -> np.ndarray:
    """1D box blur along one axis using cumulative sums. Vectorised, no Python loops."""
    k   = 2 * radius + 1
    N   = arr.shape[axis]
    pad = [(0, 0)] * arr.ndim
    pad[axis] = (radius, radius)
    padded = np.pad(arr, pad, mode='edge')

    # Prepend a zero slice so cs[i] = sum of first i elements of padded
    zero_shape       = list(padded.shape)
    zero_shape[axis] = 1
    cs = np.cumsum(
        np.concatenate([np.zeros(zero_shape, np.float32), padded], axis=axis),
        axis=axis, dtype=np.float32,
    )

    # out[j] = (cs[j+k] - cs[j]) / k  →  mean of padded[j : j+k]
    sl_hi = [slice(None)] * cs.ndim;  sl_hi[axis] = slice(k, k + N)
    sl_lo = [slice(None)] * cs.ndim;  sl_lo[axis] = slice(0, N)
    return (cs[tuple(sl_hi)] - cs[tuple(sl_lo)]) / k


# ---------------------------------------------------------------------------
# DebugDisplay
# ---------------------------------------------------------------------------

class DebugDisplay:
    """
    Pygame window that mirrors the LED matrix pixel buffer with LED glow rendering.

    Args:
        hw            : HardwareManager (imu must support inject_rotation for sim)
        state_machine : StateMachine (for stop() and window title bar)
        scale         : pixels per LED cell (default 16 → 512×512 window)
    """

    def __init__(self, hw, state_machine, scale: int = SCALE):
        self.hw    = hw
        self.sm    = state_machine
        self.scale = scale
        self._W    = 32 * scale

        # Precompute per-frame invariants
        self._mask_tiled = np.tile(_build_led_mask(scale), (32, 32))  # (W, W)
        self._bg         = np.broadcast_to(BG_COLOR, (self._W, self._W, 3)).copy()
        self._sigma      = scale * GLOW_SIGMA_FACTOR

        self._screen = None
        self._clock  = None

    # ------------------------------------------------------------------
    # Main loop — blocks until window is closed
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Pygame event loop. Starts the StateMachine after pygame is ready."""
        pygame.init()
        self._screen = pygame.display.set_mode((self._W, self._W))
        self._clock  = pygame.time.Clock()
        self._update_title()
        self.sm.start()   # start here so audio is ready before any sounds play

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_q):
                        running = False
                    else:
                        self._handle_keydown(event.key)
                elif event.type == pygame.KEYUP:
                    self._handle_keyup(event.key)

            self._render()
            self._update_title()
            self._clock.tick(FPS)

        self.sm.stop()
        self.hw.cleanup()
        pygame.quit()

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _render(self) -> None:
        """
        Build the glow-composite frame and blit it to the screen.

        Pipeline:
            pixel_data (32,32,3 uint8)
            → colors_scaled (512,512,3 float32)  — np.repeat, no loop
            → core (512,512,3 float32)            — multiply by circular LED mask
            → glow (512,512,3 float32)            — gaussian blur of core
            → result = clip(bg + glow*I + core)   — additive composite
        """
        pixel_data = self.hw.display.pixel_data.data   # (32, 32, 3) uint8

        # Upscale: each pixel fills one SCALE×SCALE cell
        colors_scaled = np.repeat(
            np.repeat(pixel_data, self.scale, axis=0), self.scale, axis=1
        ).astype(np.float32)                                             # (W, W, 3)

        # Circular LED dots: zero out the corners of each cell
        core = colors_scaled * self._mask_tiled[:, :, np.newaxis]       # (W, W, 3)

        # Glow: blur the core; adjacent LEDs' glows add together naturally
        glow = _glow_blur(core, self._sigma)

        # Additive composite — clamp to valid uint8 range
        result = np.clip(
            self._bg + glow * GLOW_INTENSITY + core, 0, 255
        ).astype(np.uint8)

        # pygame surfarray expects (width, height, 3) — transpose H↔W
        surf = pygame.surfarray.make_surface(result.transpose(1, 0, 2))
        self._screen.blit(surf, (0, 0))
        pygame.display.flip()

    def _update_title(self) -> None:
        pygame.display.set_caption(
            f"Window Device Sim  |  {self.sm.current_state_name}"
        )

    # ------------------------------------------------------------------
    # Input dispatch
    # ------------------------------------------------------------------

    def _handle_keydown(self, key) -> None:
        if key in _BUTTON_KEYS:
            self.hw.simulate_press(_BUTTON_KEYS[key])
            return
        if key in _ARROW_KEYS:
            axis, rate = _ARROW_KEYS[key]
            imu = self.hw.imu
            if hasattr(imu, 'inject_rotation'):
                imu.inject_rotation(axis, rate)

    def _handle_keyup(self, key) -> None:
        if key in _ARROW_KEYS:
            axis, _ = _ARROW_KEYS[key]
            imu = self.hw.imu
            if hasattr(imu, 'inject_rotation'):
                imu.inject_rotation(axis, 0.0)
