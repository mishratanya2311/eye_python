#!/usr/bin/env python3
"""
PROJECT: THE EYE WITHIN WORDS — Python Generative Typography Animation
======================================================================
A full-screen generative typography artwork for macOS in which 100% of the screen
is filled edge-to-edge with readable meaningful words, quotes, and poetic sentences
that collectively form the illusion of ONE enormous, living, blinking human eye,
accompanied by a continuous cinematic camera zoom between wide and close-up views.

Controls:
  SPACE : Trigger an immediate blink
  B     : Enable or disable automatic blinking
  Z     : Toggle automatic camera zooming
  C     : Change the color palette
  R     : Regenerate a new arrangement of meaningful quotes
  H     : Show or hide keyboard instructions
  ESC   : Close the animation safely
  Mouse : Subtly influences the gaze and camera focus
"""

import argparse
import math
import os
import random
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import pygame


# ============================================================================
# 1. GENERATING MEANINGFUL QUOTES & POETIC VOCABULARY
# ============================================================================

SIGNATURE_QUOTES = [
    "we are made of stars",
    "look beyond what you see",
    "every thought leaves a trace",
    "the universe lives within us",
    "beauty exists in the details",
    "we become what we believe",
    "silence has its own language",
    "nothing is ever truly invisible",
    "your perception creates your world",
    "the truth hides between the lines",
    "every ending begins somewhere",
    "consciousness observing itself",
    "there is more than meets the eye",
    "even darkness carries meaning",
    "wonder is a form of intelligence",
    "the world is written in patterns",
    "what you seek is seeking you",
    "everything is connected",
    "look closer",
    "stay curious",
]

ADDITIONAL_POETIC_QUOTES = [
    "light remembers where it has been",
    "every question opens an unseen door",
    "we are the universe becoming aware",
    "in stillness the hidden becomes clear",
    "meaning blooms where attention rests",
    "time is a river of quiet revelations",
    "beneath every surface lies another sky",
    "words are the architecture of thought",
    "to truly see is to be transformed",
    "infinite worlds inside a single glance",
    "memory is starlight traveling through mind",
    "the observer and the observed are one",
    "clarity arrives when the mind grows quiet",
    "every heartbeat echoes across eternity",
    "dreams are letters from the unseen self",
    "curiosity is the compass of the soul",
    "shadows only prove the presence of light",
    "vision begins where certainty ends",
    "all things are woven from the same light",
    "listen to the quiet between your thoughts",
    "awareness is the canvas of existence",
    "every moment contains the whole of time",
    "the eye reads what the heart remembers",
    "patterns of light become living thought",
    "seek the poetry hidden in plain sight",
    "nothing seen is ever separate from you",
    "thought is the brushstroke of reality",
    "within the finite dwells the infinite",
    "each breath is a quiet beginning",
    "truth shines brightest in the dark",
]

MEANINGFUL_SHORT_WORDS = [
    "existence", "perception", "eternity", "wonder", "look closer",
    "stay curious", "consciousness", "clarity", "horizon", "infinity",
    "presence", "silence", "radiance", "reflection", "insight",
    "empathy", "mystery", "serenity", "awakening", "harmony",
    "cosmos", "memory", "origin", "vision", "truth", "light",
    "dream", "spirit", "essence", "timeless", "intimate", "witness",
    "observer", "vivid", "lucid", "transcend", "illuminate", "connect",
    "breathe", "imagine", "perceive", "discover", "believe", "focus",
]

PUPIL_DARK_WORDS = [
    "within", "silence", "origin", "eternity", "mystery", "depth",
    "unseen", "essence", "center", "stillness", "cosmos", "infinite",
    "shadow", "secret", "truth", "existence", "source", "soul",
    "awareness", "void", "core", "unknown", "singularity", "intimate",
]

HIGHLIGHT_WORDS = [
    "light", "clarity", "wonder", "truth", "shine", "vision",
    "lucid", "spark", "pure", "awake", "vivid", "radiance",
    "star", "clear", "see", "glow", "illuminate",
]


def generate_meaningful_quotes(rng: random.Random, mode: str = "quote") -> str:
    """
    Return a genuine, correctly spelled quote, philosophical sentence, or word.
    Modes: 'quote', 'mixed', 'short', 'pupil', 'highlight'.
    """
    if mode == "highlight":
        return rng.choice(HIGHLIGHT_WORDS)
    if mode == "pupil":
        return rng.choice(PUPIL_DARK_WORDS)
    if mode == "short":
        return rng.choice(MEANINGFUL_SHORT_WORDS)
    if mode == "quote":
        if rng.random() < 0.48:
            return rng.choice(SIGNATURE_QUOTES)
        return rng.choice(ADDITIONAL_POETIC_QUOTES)

    r = rng.random()
    if r < 0.40:
        return rng.choice(SIGNATURE_QUOTES)
    elif r < 0.76:
        return rng.choice(ADDITIONAL_POETIC_QUOTES)
    else:
        return rng.choice(MEANINGFUL_SHORT_WORDS)


# ============================================================================
# 2. COLOR PALETTES & ATMOSPHERIC THEMES
# ============================================================================

@dataclass
class TypographyPalette:
    name: str
    canvas_bg: Tuple[int, int, int]
    bg_field_dark: List[Tuple[int, int, int]]      # Midnight navy & deep slate for outer field
    bg_field_orbital: List[Tuple[int, int, int]]   # Slightly brighter indigo/slate near brow/cheek
    sclera_colors: List[Tuple[int, int, int]]      # Ivory, silver, pale blue, crisp white
    iris_outer: List[Tuple[int, int, int]]         # Deep electric blue & violet limbal ring
    iris_mid: List[Tuple[int, int, int]]           # Cyan, turquoise, electric blue, violet
    iris_inner: List[Tuple[int, int, int]]         # Luminous cyan & icy-blue collarette
    iris_alt: List[Tuple[int, int, int]]           # Phase-shifted iris colors for slow breathing
    pupil_words: List[Tuple[int, int, int]]        # Dark blue, midnight navy & charcoal words
    highlight_words: List[Tuple[int, int, int]]    # Bright white & icy blue catchlights
    eyelid_rim: List[Tuple[int, int, int]]         # Silver-white, icy blue, luminous lavender
    eyelid_sheet: List[Tuple[int, int, int]]       # Slate-blue, muted violet, dusk silver
    accent_tint: Tuple[int, int, int]


PALETTES: List[TypographyPalette] = [
    TypographyPalette(
        name="Midnight Poetry — Cyan, Electric Blue & Violet",
        canvas_bg=(3, 6, 13),
        bg_field_dark=[
            (36, 58, 96), (42, 66, 108), (46, 50, 92),
            (32, 52, 86), (50, 74, 118),
        ],
        bg_field_orbital=[
            (62, 94, 148), (74, 82, 144), (56, 86, 138), (80, 110, 164),
        ],
        sclera_colors=[
            (244, 248, 255), (242, 236, 224), (208, 224, 244),
            (184, 212, 242), (228, 236, 248),
        ],
        iris_outer=[
            (32, 78, 175), (68, 52, 168), (24, 108, 168), (82, 58, 182),
        ],
        iris_mid=[
            (0, 222, 252), (22, 238, 218), (45, 155, 255),
            (118, 82, 248), (0, 198, 210), (68, 195, 255),
        ],
        iris_inner=[
            (135, 250, 255), (85, 235, 255), (185, 245, 255), (162, 138, 255),
        ],
        iris_alt=[
            (142, 78, 252), (0, 242, 218), (48, 178, 255), (178, 105, 255),
        ],
        pupil_words=[
            (28, 44, 78), (34, 52, 90), (42, 38, 82), (24, 38, 68),
        ],
        highlight_words=[
            (255, 255, 255), (222, 248, 255), (190, 240, 255),
        ],
        eyelid_rim=[
            (232, 244, 255), (196, 222, 250), (172, 206, 245), (218, 232, 252),
        ],
        eyelid_sheet=[
            (98, 136, 192), (108, 98, 172), (84, 118, 172), (124, 156, 208),
        ],
        accent_tint=(0, 195, 245),
    ),
    TypographyPalette(
        name="Bioluminescent Verse — Turquoise, Emerald & Deep Navy",
        canvas_bg=(3, 9, 12),
        bg_field_dark=[
            (30, 66, 76), (36, 74, 86), (28, 58, 72), (42, 82, 92),
        ],
        bg_field_orbital=[
            (54, 108, 118), (62, 118, 128), (48, 96, 112),
        ],
        sclera_colors=[
            (242, 250, 248), (238, 235, 224), (202, 228, 226), (178, 216, 220),
        ],
        iris_outer=[
            (16, 96, 102), (24, 76, 128), (14, 112, 92), (38, 64, 134),
        ],
        iris_mid=[
            (0, 230, 184), (20, 240, 212), (38, 188, 238), (16, 210, 152),
        ],
        iris_inner=[
            (142, 255, 228), (98, 248, 242), (182, 255, 238), (82, 238, 198),
        ],
        iris_alt=[
            (0, 198, 245), (52, 248, 168), (26, 224, 218), (112, 252, 204),
        ],
        pupil_words=[
            (22, 46, 54), (28, 54, 66), (26, 42, 62),
        ],
        highlight_words=[
            (255, 255, 255), (222, 255, 248), (188, 248, 240),
        ],
        eyelid_rim=[
            (226, 248, 244), (188, 228, 222), (164, 212, 208),
        ],
        eyelid_sheet=[
            (84, 150, 156), (74, 126, 144), (102, 166, 170),
        ],
        accent_tint=(0, 215, 175),
    ),
    TypographyPalette(
        name="Astral Manuscript — Amethyst, Starlight & Indigo",
        canvas_bg=(6, 5, 14),
        bg_field_dark=[
            (48, 44, 88), (56, 50, 98), (42, 52, 92), (62, 54, 108),
        ],
        bg_field_orbital=[
            (82, 74, 138), (74, 86, 142), (94, 82, 152),
        ],
        sclera_colors=[
            (248, 245, 254), (242, 236, 228), (216, 212, 238), (192, 206, 242),
        ],
        iris_outer=[
            (78, 42, 152), (106, 36, 142), (48, 56, 158), (92, 34, 128),
        ],
        iris_mid=[
            (176, 88, 252), (124, 112, 255), (218, 84, 228), (72, 174, 255),
        ],
        iris_inner=[
            (236, 188, 255), (196, 222, 255), (248, 204, 255), (162, 236, 255),
        ],
        iris_alt=[
            (92, 182, 255), (232, 108, 250), (154, 124, 255), (244, 144, 236),
        ],
        pupil_words=[
            (36, 28, 68), (44, 34, 80), (30, 38, 74),
        ],
        highlight_words=[
            (255, 255, 255), (245, 238, 255), (218, 242, 255),
        ],
        eyelid_rim=[
            (240, 230, 255), (208, 196, 242), (186, 204, 248),
        ],
        eyelid_sheet=[
            (128, 110, 186), (104, 120, 178), (144, 124, 198),
        ],
        accent_tint=(168, 92, 248),
    ),
]


# ============================================================================
# 3. FONT MANAGEMENT & SHARP TYPOGRAPHY RENDERING
# ============================================================================

class FontManager:
    """Loads clean, highly legible macOS fonts (Regular & Bold weights) and caches them."""

    FONT_CANDIDATES = [
        ("/System/Library/Fonts/Optima.ttc", 0, 1),
        ("/System/Library/Fonts/HelveticaNeue.ttc", 0, 1),
        ("/System/Library/Fonts/Avenir Next.ttc", 7, 2),
        ("/Library/Fonts/Arial.ttf", 0, 0),
    ]

    def __init__(self) -> None:
        self.font_path: Optional[str] = None
        self.reg_index: int = 0
        self.bold_index: int = 0
        for path, r_idx, b_idx in self.FONT_CANDIDATES:
            if os.path.exists(path):
                self.font_path = path
                self.reg_index = r_idx
                self.bold_index = b_idx
                break
        self.pil_cache: Dict[Tuple[int, bool], ImageFont.FreeTypeFont] = {}

    def get_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        size = max(7, int(size))
        key = (size, bold)
        if key not in self.pil_cache:
            if self.font_path:
                try:
                    idx = self.bold_index if bold else self.reg_index
                    self.pil_cache[key] = ImageFont.truetype(self.font_path, size, index=idx)
                except Exception:
                    self.pil_cache[key] = ImageFont.load_default()
            else:
                self.pil_cache[key] = ImageFont.load_default()
        return self.pil_cache[key]

    def measure(self, text: str, size: int, bold: bool = False) -> Tuple[float, float]:
        font = self.get_font(size, bold=bold)
        bbox = font.getbbox(text)
        return float(max(4, bbox[2] - bbox[0])), float(max(4, bbox[3] - bbox[1]))


def pil_to_pygame(pil_img: Image.Image) -> pygame.Surface:
    """Convert an RGBA PIL image to a hardware-accelerated alpha Pygame surface."""
    if pil_img.mode != "RGBA":
        pil_img = pil_img.convert("RGBA")
    return pygame.image.fromstring(pil_img.tobytes(), pil_img.size, "RGBA").convert_alpha()


def draw_word_pil(
    target_img: Image.Image,
    font_mgr: FontManager,
    text: str,
    cx: float,
    cy: float,
    font_size: int,
    angle_deg: float,
    color_rgba: Tuple[int, int, int, int],
    bold: bool = False,
) -> None:
    """Render an anti-aliased word/quote centered at `(cx, cy)` rotated by `angle_deg`."""
    font = font_mgr.get_font(font_size, bold=bold)
    bbox = font.getbbox(text)
    tw = max(1, bbox[2] - bbox[0] + 4)
    th = max(1, bbox[3] - bbox[1] + 4)

    if abs(angle_deg) <= 0.45:
        draw = ImageDraw.Draw(target_img)
        tx = int(round(cx - tw / 2.0 + 2 - bbox[0]))
        ty = int(round(cy - th / 2.0 + 2 - bbox[1]))
        draw.text((tx, ty), text, font=font, fill=color_rgba)
        return

    txt_img = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    draw = ImageDraw.Draw(txt_img)
    draw.text((2 - bbox[0], 2 - bbox[1]), text, font=font, fill=color_rgba)
    txt_img = txt_img.rotate(angle_deg, resample=Image.BICUBIC, expand=True)

    px = int(round(cx - txt_img.width / 2.0))
    py = int(round(cy - txt_img.height / 2.0))

    if px >= target_img.width or py >= target_img.height:
        return
    if px + txt_img.width <= 0 or py + txt_img.height <= 0:
        return

    src_x = max(0, -px)
    src_y = max(0, -py)
    dst_x = max(0, px)
    dst_y = max(0, py)

    if (
        src_x > 0
        or src_y > 0
        or dst_x + txt_img.width > target_img.width
        or dst_y + txt_img.height > target_img.height
    ):
        crop_w = min(txt_img.width - src_x, target_img.width - dst_x)
        crop_h = min(txt_img.height - src_y, target_img.height - dst_y)
        if crop_w <= 0 or crop_h <= 0:
            return
        txt_img = txt_img.crop((src_x, src_y, src_x + crop_w, src_y + crop_h))

    target_img.alpha_composite(txt_img, (dst_x, dst_y))


def create_word_sprite(
    font_mgr: FontManager,
    text: str,
    font_size: int,
    angle_deg: float,
    color_rgba: Tuple[int, int, int, int],
    bold: bool = False,
) -> pygame.Surface:
    font = font_mgr.get_font(font_size, bold=bold)
    bbox = font.getbbox(text)
    tw = max(1, bbox[2] - bbox[0] + 4)
    th = max(1, bbox[3] - bbox[1] + 4)
    img = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.text((2 - bbox[0], 2 - bbox[1]), text, font=font, fill=color_rgba)
    if abs(angle_deg) > 0.45:
        img = img.rotate(angle_deg, resample=Image.BICUBIC, expand=True)
    return pil_to_pygame(img)


# ============================================================================
# 4. CALCULATING THE EYE'S SPATIAL AND COLOR PATTERNS
# ============================================================================

@dataclass
class EyeCanvasGeometry:
    """
    Defines both the physical screen resolution and the larger high-resolution
    virtual typography canvas so zooming in/out is always razor-sharp and never
    exposes blank edges.
    """
    screen_w: int
    screen_h: int
    canvas_w: int
    canvas_h: int
    center_x: int
    center_y: int
    eye_half_w: float
    eye_half_h: float
    iris_radius: float
    pupil_radius: float
    scale: float


def calculate_eye_spatial_and_color_patterns(
    screen_w: int, screen_h: int
) -> EyeCanvasGeometry:
    """
    Create a virtual typography canvas 1.55x larger than the physical screen.
    In the wide camera view (zoom=1.0), the viewport shows the central ~82% of the
    virtual canvas where the giant eye fills ~90% of the screen width.
    """
    canvas_mult = 1.55
    canvas_w = int(round(screen_w * canvas_mult))
    canvas_h = int(round(screen_h * canvas_mult))
    if canvas_w % 2 == 1:
        canvas_w += 1
    if canvas_h % 2 == 1:
        canvas_h += 1

    center_x = canvas_w // 2
    center_y = canvas_h // 2

    scale = min(screen_w / 1512.0, screen_h / 982.0) * 1.18

    wide_view_w = canvas_w * 0.82
    wide_view_h = canvas_h * 0.82
    eye_half_w = wide_view_w * 0.455
    eye_half_h = wide_view_h * 0.285

    iris_radius = eye_half_h * 1.02
    pupil_radius = iris_radius * 0.34

    return EyeCanvasGeometry(
        screen_w=screen_w,
        screen_h=screen_h,
        canvas_w=canvas_w,
        canvas_h=canvas_h,
        center_x=center_x,
        center_y=center_y,
        eye_half_w=eye_half_w,
        eye_half_h=eye_half_h,
        iris_radius=iris_radius,
        pupil_radius=pupil_radius,
        scale=scale,
    )


def eval_eyelid_curves(
    u: np.ndarray,
    openness: float,
    geom: EyeCanvasGeometry,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Evaluate upper and lower eyelid vertical offsets y_upper(u), y_lower(u)
    relative to `geom.center_y` (+y is downward on screen).
    `u` in [-1.0, +1.0] spans from inner medial corner (-1) to outer lateral corner (+1).
    """
    u_clamped = np.clip(u, -1.0, 1.0)
    env = np.power(np.maximum(0.0, 1.0 - u_clamped * u_clamped), 0.76)

    upper_arch = 1.0 - 0.11 * u_clamped - 0.06 * (u_clamped ** 2)
    lower_arch = 1.0 + 0.13 * u_clamped - 0.05 * (u_clamped ** 2)

    y_upper_open = -geom.eye_half_h * 1.04 * env * upper_arch
    y_lower_open = +geom.eye_half_h * 0.88 * env * lower_arch

    medial_dip = 0.09 * geom.eye_half_h * np.exp(-((u_clamped + 0.89) / 0.20) ** 2)
    lateral_sweep = -0.06 * geom.eye_half_h * np.exp(-((u_clamped - 0.86) / 0.25) ** 2)
    corner_line = medial_dip + lateral_sweep

    y_upper_open += corner_line
    y_lower_open += corner_line

    # Closed eye curve: gentle downward-sloping sleeping curve
    y_closed = geom.eye_half_h * 0.16 * env + corner_line

    t = float(np.clip(openness, 0.0, 1.0))
    y_upper = y_closed * (1.0 - t) + y_upper_open * t
    y_lower = y_closed * (1.0 - t) + y_lower_open * t
    return y_upper, y_lower


def eval_field_streamline_y(
    x_arr: np.ndarray,
    base_y_offset: float,
    geom: EyeCanvasGeometry,
) -> np.ndarray:
    """
    Smooth, continuous streamline function across the entire virtual canvas.
    Wait: notice that `arch_push` is proportional to `base_y_offset`, so as
    `base_y_offset -> 0`, `arch_push -> 0` smoothly with ZERO discontinuity or gaps!
    Every row of poetry is continuous and evenly spaced across 100% of the canvas.
    """
    u = (x_arr - geom.center_x) / geom.eye_half_w
    gaussian_bell = np.exp(-0.5 * (u / 0.76) ** 2)
    norm_y = abs(base_y_offset) / max(1.0, geom.eye_half_h)
    dist_atten = np.exp(-norm_y / 1.85)
    arch_push = base_y_offset * 0.42 * gaussian_bell * dist_atten
    return geom.center_y + base_y_offset + arch_push


# ============================================================================
# 5. LAYING OUT READABLE TEXT ACROSS THE ENTIRE VIRTUAL CANVAS
# ============================================================================

def layout_full_canvas_typography(
    geom: EyeCanvasGeometry,
    font_mgr: FontManager,
    palette: TypographyPalette,
    rng: random.Random,
) -> Tuple[pygame.Surface, pygame.Surface, pygame.Surface]:
    """
    Populate 100% of the virtual canvas with non-overlapping, readable quotes and words:
      1. `full_field_surf`: Covers 100% of `(canvas_w, canvas_h)` from edge to edge and
         corner to corner with zero gaps.
         - Outside the eye contour: shaded in midnight navy, slate blue, and orbital indigo.
         - Along the eyelid folds and inside the eye footprint (revealed during a blink!):
           shaded in luminous eyelid-sheet and eyelid-rim typography, including a bright
           curved horizontal band of words along the closed-eyelid seam!
      2. `sclera_surf`: Bright ivory, silver-white, and icy-blue readable quotes filling
         the eyeball interior with 3D spherical shading.
      3. `iris_cutout_mask`: Circular cutout so sclera quotes do not bleed behind the iris.
    """
    # ------------------------------------------------------------------------
    # A. FULL-CANVAS WALL OF POETRY (100% Edge-to-Edge Coverage, Zero Blank Areas)
    # ------------------------------------------------------------------------
    field_pil = Image.new("RGBA", (geom.canvas_w, geom.canvas_h), (*palette.canvas_bg, 255))

    row_spacing = max(16.0, 18.0 * geom.scale)
    max_y_extent = geom.canvas_h * 0.54
    y_offsets = np.arange(-max_y_extent, max_y_extent + row_spacing, row_spacing)

    for r_idx, base_y_off in enumerate(y_offsets):
        if r_idx % 4 == 0:
            fsize = max(10, int(12.8 * geom.scale))
        elif r_idx % 2 == 0:
            fsize = max(9, int(11.4 * geom.scale))
        else:
            fsize = max(8, int(10.2 * geom.scale))

        x_cursor = 6.0 + rng.uniform(0.0, 18.0)
        while x_cursor < geom.canvas_w - 8.0:
            text = generate_meaningful_quotes(rng, "mixed")
            is_bold = (r_idx % 5 == 0)
            w_px, _ = font_mgr.measure(text, fsize, bold=is_bold)
            gap_px = max(10.0, 12.0 * geom.scale)
            wx = x_cursor + w_px * 0.5

            if wx - w_px * 0.5 > geom.canvas_w:
                break

            x_sample = np.array([wx - 12.0, wx, wx + 12.0])
            y_sample = eval_field_streamline_y(x_sample, float(base_y_off), geom)
            wy = float(y_sample[1])

            if -20.0 <= wy <= geom.canvas_h + 20.0:
                slope = float(y_sample[2] - y_sample[0]) / 24.0
                angle = -math.degrees(math.atan(slope))

                u_rel = (wx - geom.center_x) / geom.eye_half_w
                v_rel = (wy - geom.center_y) / geom.eye_half_h
                elliptical_dist = math.hypot(u_rel * 0.88, v_rel * 0.78)

                # Evaluate open & closed eyelid curves at u_rel to sculpt the eyelid & brow anatomy
                yu_arr, yl_arr = eval_eyelid_curves(np.array([u_rel]), 1.0, geom)
                yc_arr, _ = eval_eyelid_curves(np.array([u_rel]), 0.0, geom)
                yu_open = float(yu_arr[0])
                yl_open = float(yl_arr[0])
                y_closed = float(yc_arr[0])
                dy_from_center = wy - geom.center_y

                if abs(u_rel) <= 1.03 and (yu_open - 46.0 * geom.scale) <= dy_from_center <= (yl_open + 42.0 * geom.scale):
                    # Inside the Eyelid / Palpebral Region (including what is revealed when the eye closes!)
                    dist_to_closed_seam = abs(dy_from_center - y_closed)
                    dist_to_upper_open = abs(dy_from_center - yu_open)
                    dist_to_lower_open = abs(dy_from_center - yl_open)

                    if dist_to_closed_seam < 15.0 * geom.scale:
                        # Luminous narrow curved line of words at complete eyelid closure!
                        col = rng.choice(palette.eyelid_rim)
                        shade = 1.0
                        alpha = 252
                        is_bold = True
                    elif dist_to_upper_open < 24.0 * geom.scale or dist_to_lower_open < 22.0 * geom.scale:
                        # Bright upper & lower eyelid contour bands framing the eye
                        col = rng.choice(palette.eyelid_rim)
                        shade = 0.92
                        alpha = rng.randint(225, 250)
                        is_bold = True
                    else:
                        # Eyelid fold typography (visible as the upper eyelid descends during blinks)
                        col = rng.choice(palette.eyelid_sheet)
                        shade = max(0.68, 1.0 - 0.25 * abs(u_rel))
                        alpha = rng.randint(205, 240)
                elif elliptical_dist < 1.58:
                    # Surrounding orbital brow & cheekbone typography
                    col = rng.choice(palette.bg_field_orbital)
                    t_halo = max(0.0, (elliptical_dist - 1.0) / 0.58)
                    shade = 1.0 - 0.24 * t_halo
                    alpha = rng.randint(205, 240)
                else:
                    # Outer full-screen typography field extending to all 4 corners
                    col = rng.choice(palette.bg_field_dark)
                    wave = 0.88 + 0.12 * math.sin(u_rel * 2.0 + v_rel * 1.6)
                    shade = wave
                    alpha = rng.randint(200, 238)

                r = int(min(255, col[0] * shade))
                g = int(min(255, col[1] * shade))
                b = int(min(255, col[2] * shade))
                draw_word_pil(
                    field_pil, font_mgr, text, wx, wy, fsize, angle, (r, g, b, alpha), bold=is_bold
                )

            x_cursor += w_px + gap_px

    # ------------------------------------------------------------------------
    # B. SCLERA TYPOGRAPHY (Readable Ivory, Silver, Pale Blue & White Quotes)
    # ------------------------------------------------------------------------
    sclera_pil = Image.new("RGBA", (geom.canvas_w, geom.canvas_h), (0, 0, 0, 0))
    sclera_bg_draw = ImageDraw.Draw(sclera_pil)
    u_poly = np.linspace(-1.0, 1.0, 96)
    yu_p, yl_p = eval_eyelid_curves(u_poly, 1.0, geom)
    xp = geom.center_x + u_poly * geom.eye_half_w
    pts_open = list(zip(xp.tolist(), (geom.center_y + yu_p).tolist())) + list(
        zip(xp[::-1].tolist(), (geom.center_y + yl_p[::-1]).tolist())
    )
    sclera_bg_draw.polygon(pts_open, fill=(6, 11, 22, 250))

    n_sclera_rows = 28
    for row_idx in range(n_sclera_rows):
        v_frac = (row_idx + 0.5) / n_sclera_rows
        fsize = max(9, int((10.2 + 3.6 * math.sin(v_frac * math.pi)) * geom.scale))
        u_cursor = -0.97 + rng.uniform(0.0, 0.025)

        while u_cursor < 0.97:
            mode = "short" if abs(u_cursor) > 0.74 else "mixed"
            quote = generate_meaningful_quotes(rng, mode)
            is_bold = (row_idx % 4 == 0)
            w_px, _ = font_mgr.measure(quote, fsize, bold=is_bold)
            du = (w_px + 8.0 * geom.scale) / geom.eye_half_w
            u_mid = u_cursor + du * 0.5
            if u_mid > 0.97:
                break

            y_u_arr, y_l_arr = eval_eyelid_curves(
                np.array([u_mid - 0.025, u_mid, u_mid + 0.025]), 1.0, geom
            )
            yu, yl = float(y_u_arr[1]), float(y_l_arr[1])
            if yl - yu < fsize * 0.75:
                u_cursor += du * 0.65
                continue

            wy_rel = yu + v_frac * (yl - yu)
            wx_rel = u_mid * geom.eye_half_w

            y0 = float(y_u_arr[0] + v_frac * (y_l_arr[0] - y_u_arr[0]))
            y2 = float(y_u_arr[2] + v_frac * (y_l_arr[2] - y_u_arr[2]))
            slope = (y2 - y0) / (0.05 * geom.eye_half_w)
            angle = -math.degrees(math.atan(slope))

            dist_x = abs(u_mid)
            dist_y = abs(v_frac - 0.52) * 1.7
            sphere_shade = max(
                0.38,
                min(1.0, 1.16 - 0.62 * (dist_x ** 1.55) - 0.22 * (dist_y ** 1.5)),
            )
            lid_shadow = min(1.0, 0.56 + 0.70 * v_frac)
            brightness = sphere_shade * lid_shadow

            base_col = rng.choice(palette.sclera_colors)
            r = int(min(255, base_col[0] * brightness))
            g = int(min(255, base_col[1] * brightness))
            b = int(min(255, base_col[2] * brightness))
            alpha = int(min(255, 205 + 50 * brightness))

            wx = geom.center_x + wx_rel
            wy = geom.center_y + wy_rel
            draw_word_pil(
                sclera_pil, font_mgr, quote, wx, wy, fsize, angle, (r, g, b, alpha), bold=is_bold
            )
            u_cursor += du

    # Circular cutout mask so sclera quotes don't bleed behind the iris & pupil
    cutout_dim = int(geom.iris_radius * 2.25)
    cutout_pil = Image.new("RGBA", (cutout_dim, cutout_dim), (255, 255, 255, 255))
    c_draw = ImageDraw.Draw(cutout_pil)
    cr = int(geom.iris_radius * 0.97)
    cc = cutout_dim // 2
    c_draw.ellipse((cc - cr, cc - cr, cc + cr, cc + cr), fill=(0, 0, 0, 10))
    cutout_pil = cutout_pil.filter(ImageFilter.GaussianBlur(radius=max(3, int(7 * geom.scale))))

    return (
        pil_to_pygame(field_pil),
        pil_to_pygame(sclera_pil),
        pil_to_pygame(cutout_pil),
    )


# ============================================================================
# 6. CREATING THE IRIS, PUPIL & HIGHLIGHTS FROM TYPOGRAPHY
# ============================================================================

def create_iris_and_pupil_typography(
    geom: EyeCanvasGeometry,
    font_mgr: FontManager,
    palette: TypographyPalette,
    rng: random.Random,
) -> Dict[str, pygame.Surface]:
    """
    Build the giant Iris, Pupil, and Highlights from clean, non-overlapping
    circular and radial arrangements of real words.
    """
    iris_dim = int(geom.iris_radius * 2.38)
    if iris_dim % 2 == 1:
        iris_dim += 1
    icx = iris_dim // 2
    icy = iris_dim // 2

    rings_pil_a = Image.new("RGBA", (iris_dim, iris_dim), (0, 0, 0, 0))
    rings_pil_b = Image.new("RGBA", (iris_dim, iris_dim), (0, 0, 0, 0))

    for pil_disc in (rings_pil_a, rings_pil_b):
        d_draw = ImageDraw.Draw(pil_disc)
        ir_px = int(geom.iris_radius * 0.98)
        d_draw.ellipse(
            (icx - ir_px, icy - ir_px, icx + ir_px, icy + ir_px),
            fill=(5, 10, 22, 244),
        )

    # 1. CONCENTRIC IRIS RINGS (15 cleanly spaced concentric word rings)
    ring_fracs = np.linspace(0.96, 0.37, 15)
    for r_idx, r_frac_val in enumerate(ring_fracs):
        r_frac = float(r_frac_val)
        rad = geom.iris_radius * r_frac
        fsize = max(8, int((8.8 + (1.0 - r_frac) * 4.2) * geom.scale))
        is_bold = (r_idx % 3 == 0)
        theta_cur = rng.uniform(0, math.tau)
        theta_end = theta_cur + math.tau - 0.03

        while theta_cur < theta_end:
            word = generate_meaningful_quotes(rng, "short" if r_frac < 0.58 else "mixed")
            if len(word) > 22:
                word = generate_meaningful_quotes(rng, "short")
            w_px, _ = font_mgr.measure(word, fsize, bold=is_bold)
            d_theta = (w_px + 6.0 * geom.scale) / max(24.0, rad)
            theta_mid = theta_cur + d_theta * 0.5
            if theta_mid > theta_end:
                break

            wx = icx + rad * math.cos(theta_mid)
            wy = icy + rad * math.sin(theta_mid)

            deg_tangent = -math.degrees(theta_mid) - 90.0
            if 90 < (deg_tangent % 360) < 270:
                deg_tangent += 180.0

            if r_frac > 0.84:
                col_a = rng.choice(palette.iris_outer)
                col_b = rng.choice(palette.iris_mid)
                alpha = 248
            elif r_frac > 0.48:
                col_a = rng.choice(palette.iris_mid)
                col_b = rng.choice(palette.iris_alt)
                alpha = 252
            else:
                col_a = rng.choice(palette.iris_inner)
                col_b = rng.choice(palette.iris_alt)
                alpha = 255

            draw_word_pil(
                rings_pil_a, font_mgr, word, wx, wy, fsize, deg_tangent, (*col_a, alpha), bold=is_bold
            )
            draw_word_pil(
                rings_pil_b, font_mgr, word, wx, wy, fsize, deg_tangent, (*col_b, alpha), bold=is_bold
            )
            theta_cur += d_theta

    # 2. RADIAL IRIS SPOKES (84 radial words in electric blue, cyan, and violet)
    radial_pil_a = Image.new("RGBA", (iris_dim, iris_dim), (0, 0, 0, 0))
    radial_pil_b = Image.new("RGBA", (iris_dim, iris_dim), (0, 0, 0, 0))
    n_spokes = 84
    for s_idx in range(n_spokes):
        theta = (s_idx / n_spokes) * math.tau + rng.uniform(-0.015, 0.015)
        r_band = rng.uniform(0.46, 0.84)
        rad = geom.iris_radius * r_band
        wx = icx + rad * math.cos(theta)
        wy = icy + rad * math.sin(theta)

        deg_radial = -math.degrees(theta)
        if 90 < (deg_radial % 360) < 270:
            deg_radial += 180.0

        word = generate_meaningful_quotes(rng, "short")
        fsize = max(8, int(rng.uniform(8.2, 11.0) * geom.scale))
        col_a = rng.choice(palette.iris_inner if r_band < 0.60 else palette.iris_mid)
        col_b = rng.choice(palette.iris_alt)
        alpha = rng.randint(165, 225)

        draw_word_pil(radial_pil_a, font_mgr, word, wx, wy, fsize, deg_radial, (*col_a, alpha))
        draw_word_pil(radial_pil_b, font_mgr, word, wx, wy, fsize, deg_radial, (*col_b, alpha))

    # Clear the circular pupil center inside the iris layers
    pupil_cut = Image.new("L", (iris_dim, iris_dim), 255)
    pm_draw = ImageDraw.Draw(pupil_cut)
    pr_clear = int(geom.pupil_radius * 0.98)
    pm_draw.ellipse((icx - pr_clear, icy - pr_clear, icx + pr_clear, icy + pr_clear), fill=0)
    pupil_cut = pupil_cut.filter(ImageFilter.GaussianBlur(radius=max(2, int(3 * geom.scale))))
    zero_l = Image.new("L", (iris_dim, iris_dim), 0)

    for layer in (rings_pil_a, rings_pil_b, radial_pil_a, radial_pil_b):
        layer.putalpha(Image.composite(layer.getchannel("A"), zero_l, pupil_cut))

    glow_pil = rings_pil_a.filter(ImageFilter.GaussianBlur(radius=max(4, int(10 * geom.scale))))

    # 3. PUPIL TYPOGRAPHY (Dense concentric rings of readable dark-blue & charcoal words)
    pupil_dim = int(geom.pupil_radius * 2.45)
    if pupil_dim % 2 == 1:
        pupil_dim += 1
    pcx = pupil_dim // 2
    pcy = pupil_dim // 2
    pupil_pil = Image.new("RGBA", (pupil_dim, pupil_dim), (0, 0, 0, 0))

    p_draw = ImageDraw.Draw(pupil_pil)
    pr_disc = int(geom.pupil_radius * 0.97)
    p_draw.ellipse(
        (pcx - pr_disc, pcy - pr_disc, pcx + pr_disc, pcy + pr_disc),
        fill=(3, 5, 11, 248),
    )

    for p_frac in (0.88, 0.72, 0.56, 0.40, 0.24):
        rad_p = geom.pupil_radius * p_frac
        fsize = max(7, int((8.2 + (1.0 - p_frac) * 1.8) * geom.scale))
        th_cur = rng.uniform(0, math.tau)
        th_end = th_cur + math.tau - 0.06
        while th_cur < th_end:
            word = generate_meaningful_quotes(rng, "pupil")
            w_px, _ = font_mgr.measure(word, fsize)
            d_th = max(0.32, (w_px + 4.5 * geom.scale) / max(12.0, rad_p))
            th_mid = th_cur + d_th * 0.5
            if th_mid > th_end:
                break
            wx = pcx + rad_p * math.cos(th_mid)
            wy = pcy + rad_p * math.sin(th_mid)
            deg = -math.degrees(th_mid) - 90.0
            if 90 < (deg % 360) < 270:
                deg += 180.0
            col = rng.choice(palette.pupil_words)
            vis_col = (min(255, col[0] + 26), min(255, col[1] + 40), min(255, col[2] + 68))
            draw_word_pil(pupil_pil, font_mgr, word, wx, wy, fsize, deg, (*vis_col, 255))
            th_cur += d_th

    center_word = rng.choice(["consciousness", "look within", "existence", "eternity"])
    draw_word_pil(
        pupil_pil, font_mgr, center_word, pcx, pcy,
        max(8, int(9.2 * geom.scale)), 0.0, (62, 92, 148, 255), bold=True
    )

    # 4. HIGHLIGHTS (Tiny but real words in bright white and icy blue)
    hl_pil = Image.new("RGBA", (iris_dim, iris_dim), (0, 0, 0, 0))
    hl1_cx = icx - geom.iris_radius * 0.34
    hl1_cy = icy - geom.iris_radius * 0.32
    for row_h in range(-2, 3):
        for col_h in range(-1, 2):
            word = generate_meaningful_quotes(rng, "highlight")
            fsize = max(8, int((10.5 - abs(row_h) * 0.5) * geom.scale))
            col = rng.choice(palette.highlight_words)
            dx_h = col_h * 34.0 * geom.scale
            dy_h = row_h * 14.0 * geom.scale
            ang_rad = math.radians(-24.0)
            rx = dx_h * math.cos(ang_rad) - dy_h * math.sin(ang_rad)
            ry = dx_h * math.sin(ang_rad) + dy_h * math.cos(ang_rad)
            alpha = int(max(195, 255 - (abs(row_h) * 18 + abs(col_h) * 16)))
            draw_word_pil(
                hl_pil, font_mgr, word, hl1_cx + rx, hl1_cy + ry, fsize, -24.0, (*col, alpha), bold=True
            )

    hl2_cx = icx + geom.iris_radius * 0.36
    hl2_cy = icy + geom.iris_radius * 0.35
    for k_h in range(-2, 3):
        word = generate_meaningful_quotes(rng, "highlight")
        fsize = max(7, int(9.0 * geom.scale))
        col = rng.choice(palette.highlight_words)
        dx_h = k_h * 28.0 * geom.scale
        dy_h = -abs(k_h) * 3.5 * geom.scale
        ang_rad = math.radians(-28.0)
        rx = dx_h * math.cos(ang_rad) - dy_h * math.sin(ang_rad)
        ry = dx_h * math.sin(ang_rad) + dy_h * math.cos(ang_rad)
        draw_word_pil(
            hl_pil, font_mgr, word, hl2_cx + rx, hl2_cy + ry, fsize, -28.0, (*col, 225), bold=True
        )

    return {
        "rings_a": pil_to_pygame(rings_pil_a),
        "rings_b": pil_to_pygame(rings_pil_b),
        "radial_a": pil_to_pygame(radial_pil_a),
        "radial_b": pil_to_pygame(radial_pil_b),
        "pupil": pil_to_pygame(pupil_pil),
        "highlights": pil_to_pygame(hl_pil),
        "glow": pil_to_pygame(glow_pil),
    }


# ============================================================================
# 7. CREATING ANIMATED EYELIDS AND BLINK MASKS
# ============================================================================

@dataclass
class EyelidRimWord:
    """A single crisp, non-overlapping word along the moving upper or lower eyelid rim."""
    u: float
    v_offset: float
    is_upper: bool
    surfaces: List[pygame.Surface]  # [closed_angle_surf, mid_angle_surf, open_angle_surf]


def create_animated_eyelids_and_masks(
    geom: EyeCanvasGeometry,
    font_mgr: FontManager,
    palette: TypographyPalette,
    rng: random.Random,
) -> List[EyelidRimWord]:
    """
    Create a single clean, non-overlapping upper eyelid margin stream and lower eyelid
    margin stream that travel along the exact eyelid edge during blinks, with arc-length
    stepping so adjacent words never collide or overlap.
    """
    rim_words: List[EyelidRimWord] = []

    u_grid = np.linspace(-1.02, 1.02, 160)
    dx_grid = (u_grid[1] - u_grid[0]) * geom.eye_half_w
    yu_open, yl_open = eval_eyelid_curves(u_grid, 1.0, geom)
    yu_mid, yl_mid = eval_eyelid_curves(u_grid, 0.45, geom)
    yu_closed, yl_closed = eval_eyelid_curves(u_grid, 0.0, geom)

    slope_u_open = np.gradient(yu_open, dx_grid)
    slope_u_mid = np.gradient(yu_mid, dx_grid)
    slope_u_closed = np.gradient(yu_closed, dx_grid)

    slope_l_open = np.gradient(yl_open, dx_grid)
    slope_l_mid = np.gradient(yl_mid, dx_grid)
    slope_l_closed = np.gradient(yl_closed, dx_grid)

    def build_clean_rim_stream(is_upper: bool, v_off: float, fsize: int) -> None:
        u_cur = -0.98 + rng.uniform(0.0, 0.02)
        while u_cur < 0.98:
            phrase = generate_meaningful_quotes(rng, "short" if abs(u_cur) > 0.65 else "mixed")
            if len(phrase) > 22:
                phrase = generate_meaningful_quotes(rng, "short")
            w_px, _ = font_mgr.measure(phrase, fsize, bold=True)

            idx_est = int(np.clip(((u_cur + 1.02) / 2.04) * (len(u_grid) - 1), 0, len(u_grid) - 1))
            local_slope = float(slope_u_open[idx_est] if is_upper else slope_l_open[idx_est])
            # Convert arc-length step along the sloped curve to horizontal step du
            cos_theta = 1.0 / math.sqrt(1.0 + local_slope * local_slope)
            du = ((w_px + 12.0 * geom.scale) * max(0.65, cos_theta)) / geom.eye_half_w
            u_mid = u_cur + du * 0.5
            if u_mid > 0.98:
                break

            idx = int(np.clip(((u_mid + 1.02) / 2.04) * (len(u_grid) - 1), 0, len(u_grid) - 1))
            if is_upper:
                ang_open = -math.degrees(math.atan(float(slope_u_open[idx])))
                ang_mid = -math.degrees(math.atan(float(slope_u_mid[idx])))
                ang_closed = -math.degrees(math.atan(float(slope_u_closed[idx])))
            else:
                ang_open = -math.degrees(math.atan(float(slope_l_open[idx])))
                ang_mid = -math.degrees(math.atan(float(slope_l_mid[idx])))
                ang_closed = -math.degrees(math.atan(float(slope_l_closed[idx])))

            col = rng.choice(palette.eyelid_rim)
            edge_atten = max(0.45, 1.0 - 0.50 * (abs(u_mid) ** 2.4))
            alpha = int(250 * edge_atten)

            surfs = [
                create_word_sprite(font_mgr, phrase, fsize, ang_closed, (*col, alpha), bold=True),
                create_word_sprite(font_mgr, phrase, fsize, ang_mid, (*col, alpha), bold=True),
                create_word_sprite(font_mgr, phrase, fsize, ang_open, (*col, alpha), bold=True),
            ]
            rim_words.append(
                EyelidRimWord(
                    u=u_mid,
                    v_offset=v_off,
                    is_upper=is_upper,
                    surfaces=surfs,
                )
            )
            u_cur += du

    # Single crisp upper rim stream (-9px above upper edge) and lower rim stream (+9px below lower edge)
    build_clean_rim_stream(True, -9.0 * geom.scale, max(10, int(12.2 * geom.scale)))
    build_clean_rim_stream(False, +9.0 * geom.scale, max(10, int(11.6 * geom.scale)))

    return rim_words


class BlinkController:
    """
    Natural biological blink controller (every 3-6 seconds with occasional double blinks).
    """

    def __init__(self) -> None:
        self.auto_blink: bool = True
        self.is_blinking: bool = False
        self.blink_start: float = 0.0
        self.close_dur: float = 0.125
        self.hold_dur: float = 0.045
        self.open_dur: float = 0.225
        self.queued_double: bool = False
        self.next_blink_time: float = time.perf_counter() + random.uniform(2.5, 4.5)

    def trigger_blink(self, now: Optional[float] = None, allow_double: bool = True) -> None:
        if now is None:
            now = time.perf_counter()
        self.is_blinking = True
        self.blink_start = now
        self.close_dur = random.uniform(0.115, 0.140)
        self.hold_dur = random.uniform(0.038, 0.058)
        self.open_dur = random.uniform(0.200, 0.260)
        self.queued_double = allow_double and (random.random() < 0.24)
        self.next_blink_time = now + random.uniform(3.0, 6.0)

    def update(self, now: float) -> float:
        if self.auto_blink and not self.is_blinking and now >= self.next_blink_time:
            self.trigger_blink(now, allow_double=True)

        if not self.is_blinking:
            return 1.0

        elapsed = now - self.blink_start
        total = self.close_dur + self.hold_dur + self.open_dur

        if elapsed < 0.0:
            return 1.0
        if elapsed < self.close_dur:
            u = elapsed / self.close_dur
            ease = 3.0 * (u ** 2) - 2.0 * (u ** 3)
            return max(0.0, 1.0 - ease)
        elif elapsed < self.close_dur + self.hold_dur:
            return 0.0
        elif elapsed < total:
            u = (elapsed - self.close_dur - self.hold_dur) / self.open_dur
            ease = 1.0 - (1.0 - u) ** 2.6
            return min(1.0, ease)
        else:
            if self.queued_double:
                self.queued_double = False
                self.trigger_blink(now + 0.045, allow_double=False)
            else:
                self.is_blinking = False
            return 1.0


# ============================================================================
# 8. MANAGING CINEMATIC ZOOM AND CAMERA MOVEMENT
# ============================================================================

class CinematicCamera:
    """
    Manages continuous, smooth camera zoom and gentle panning between:
      - Wide View (zoom = 1.0): The entire giant eye emerges from the edge-to-edge wall of typography.
      - Close-Up View (zoom up to 2.55x): Zooms deeply into the typography to reveal
        individual readable quotes and words without ever exposing blank edges.
    """

    def __init__(self) -> None:
        self.auto_zoom: bool = True
        self.zoom: float = 1.0
        self.phase: float = 0.0
        self.pan_x: float = 0.0
        self.pan_y: float = 0.0
        self.gaze_x: float = 0.0
        self.gaze_y: float = 0.0
        self.last_mouse_pos: Tuple[int, int] = (0, 0)
        self.last_mouse_time: float = 0.0

    def manage_zoom_and_camera(
        self,
        geom: EyeCanvasGeometry,
        now: float,
        dt: float,
        override_zoom: Optional[float] = None,
    ) -> Tuple[pygame.Rect, float, float]:
        mx, my = pygame.mouse.get_pos()
        if (mx, my) != self.last_mouse_pos:
            self.last_mouse_pos = (mx, my)
            self.last_mouse_time = now

        max_gx = geom.screen_w * 0.022
        max_gy = geom.screen_h * 0.018
        if now - self.last_mouse_time < 4.5:
            nx = (mx - geom.screen_w * 0.5) / max(1.0, geom.screen_w * 0.5)
            ny = (my - geom.screen_h * 0.5) / max(1.0, geom.screen_h * 0.5)
            target_gx = float(np.clip(nx, -1.0, 1.0)) * max_gx
            target_gy = float(np.clip(ny, -1.0, 1.0)) * max_gy
        else:
            target_gx = math.sin(now * 0.45) * math.cos(now * 0.21) * (max_gx * 0.45)
            target_gy = math.sin(now * 0.32 + 1.1) * (max_gy * 0.40)

        smooth = min(1.0, dt * 5.5)
        self.gaze_x += (target_gx - self.gaze_x) * smooth
        self.gaze_y += (target_gy - self.gaze_y) * smooth

        if override_zoom is not None:
            self.zoom = override_zoom
        elif self.auto_zoom:
            speed_mod = 0.34 + 0.08 * math.sin(now * 0.17)
            self.phase += dt * speed_mod
            raw_wave = 0.5 - 0.5 * math.cos(self.phase)
            eased = raw_wave * raw_wave * (3.0 - 2.0 * raw_wave)
            self.zoom = 1.0 + eased * 1.55
        else:
            self.zoom += (1.0 - self.zoom) * min(1.0, dt * 4.0)

        base_vw = geom.canvas_w * 0.82
        base_vh = geom.canvas_h * 0.82

        view_w = int(round(base_vw / self.zoom))
        view_h = int(round(base_vh / self.zoom))
        view_w = max(320, min(geom.canvas_w, view_w))
        view_h = max(200, min(geom.canvas_h, view_h))

        zoom_factor = (self.zoom - 1.0) / 1.55
        drift_radius_x = geom.eye_half_w * 0.30 * zoom_factor
        drift_radius_y = geom.eye_half_h * 0.25 * zoom_factor

        target_px = math.sin(now * 0.23) * drift_radius_x + self.gaze_x * 1.4
        target_py = math.cos(now * 0.19) * drift_radius_y + self.gaze_y * 1.4
        self.pan_x += (target_px - self.pan_x) * min(1.0, dt * 3.5)
        self.pan_y += (target_py - self.pan_y) * min(1.0, dt * 3.5)

        cam_cx = int(round(geom.center_x + self.pan_x))
        cam_cy = int(round(geom.center_y + self.pan_y))

        left = max(0, min(geom.canvas_w - view_w, cam_cx - view_w // 2))
        top = max(0, min(geom.canvas_h - view_h, cam_cy - view_h // 2))

        return pygame.Rect(left, top, view_w, view_h), self.gaze_x, self.gaze_y


# ============================================================================
# 9. RENDERING THE FINAL FULL-SCREEN COMPOSITION
# ============================================================================

class EyeWithinWordsApp:
    """Full-screen generative typography application."""

    def __init__(
        self,
        windowed: bool = False,
        test_frames: int = 0,
        screenshot_dir: Optional[str] = None,
    ) -> None:
        pygame.display.init()

        self.windowed = windowed
        self.test_frames = test_frames
        self.screenshot_dir = screenshot_dir

        info = pygame.display.Info()
        desktop_w = info.current_w if info.current_w > 0 else 1512
        desktop_h = info.current_h if info.current_h > 0 else 982

        if not self.windowed:
            flags = pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
            self.screen = pygame.display.set_mode((0, 0), flags)
        else:
            win_w = min(1440, int(desktop_w * 0.88))
            win_h = min(900, int(desktop_h * 0.88))
            flags = pygame.RESIZABLE | pygame.DOUBLEBUF
            self.screen = pygame.display.set_mode((win_w, win_h), flags)

        pygame.display.set_caption("THE EYE WITHIN WORDS — Generative Typography Animation")

        self.font_mgr = FontManager()
        self.palette_idx = 0
        self.seed = random.randint(10000, 999999)
        self.blink_ctrl = BlinkController()
        self.camera = CinematicCamera()
        self.show_help = False
        self.clock = pygame.time.Clock()

        self.geom: EyeCanvasGeometry = calculate_eye_spatial_and_color_patterns(
            *self.screen.get_size()
        )
        self.full_field_surf: Optional[pygame.Surface] = None
        self.sclera_surf: Optional[pygame.Surface] = None
        self.iris_cutout_mask: Optional[pygame.Surface] = None
        self.iris_layers: Dict[str, pygame.Surface] = {}
        self.eyelid_rim_words: List[EyelidRimWord] = []

        self.virtual_frame_surf: Optional[pygame.Surface] = None
        self.eye_box_canvas: Optional[pygame.Surface] = None
        self.eye_box_mask: Optional[pygame.Surface] = None
        self.eye_box_rect: pygame.Rect = pygame.Rect(0, 0, 10, 10)
        self.mask_u = np.linspace(-1.01, 1.01, 96)

        self._build_all_layers()

    def _build_all_layers(self) -> None:
        """Precompute all high-resolution typography surfaces across the virtual canvas."""
        sw, sh = self.screen.get_size()
        self.geom = calculate_eye_spatial_and_color_patterns(sw, sh)
        palette = PALETTES[self.palette_idx]
        rng = random.Random(self.seed)

        (
            self.full_field_surf,
            self.sclera_surf,
            self.iris_cutout_mask,
        ) = layout_full_canvas_typography(self.geom, self.font_mgr, palette, rng)

        self.iris_layers = create_iris_and_pupil_typography(
            self.geom, self.font_mgr, palette, rng
        )
        self.eyelid_rim_words = create_animated_eyelids_and_masks(
            self.geom, self.font_mgr, palette, rng
        )

        # Use SRCALPHA on virtual_frame_surf so per-pixel alpha blits are 100% artifact-free
        self.virtual_frame_surf = pygame.Surface(
            (self.geom.canvas_w, self.geom.canvas_h), pygame.SRCALPHA
        )

        box_w = int(self.geom.eye_half_w * 2.25)
        box_h = int(self.geom.eye_half_h * 2.65)
        box_left = self.geom.center_x - box_w // 2
        box_top = self.geom.center_y - box_h // 2
        self.eye_box_rect = pygame.Rect(box_left, box_top, box_w, box_h)
        self.eye_box_canvas = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        self.eye_box_mask = pygame.Surface((box_w, box_h), pygame.SRCALPHA)

    def render_fullscreen_composition(
        self,
        openness: float,
        cam_rect: pygame.Rect,
        gaze_x: float,
        gaze_y: float,
        now: float,
    ) -> None:
        """
        Composite the full-canvas typography, living iris/pupil, and animated blink
        on the virtual canvas, then apply the camera zoom transformation to the screen.
        """
        if self.virtual_frame_surf is None or self.full_field_surf is None:
            return

        geom = self.geom
        bx, by, _, _ = self.eye_box_rect
        local_cx = geom.center_x - bx
        local_cy = geom.center_y - by

        # 1. Blit the 100% edge-to-edge full-canvas wall of quotes (zero gaps anywhere!)
        self.virtual_frame_surf.blit(self.full_field_surf, (0, 0))

        # 2. Composite the eye interior (Sclera + Iris + Pupil + Highlights) within eye_box_canvas
        if openness > 0.012 and self.eye_box_canvas is not None and self.eye_box_mask is not None:
            self.eye_box_canvas.fill((0, 0, 0, 0))

            sclera_dx = int(gaze_x * 0.25)
            sclera_dy = int(gaze_y * 0.22)
            if self.sclera_surf is not None:
                self.eye_box_canvas.blit(
                    self.sclera_surf,
                    (sclera_dx, sclera_dy),
                    area=self.eye_box_rect,
                )

            iris_cx = local_cx + int(gaze_x)
            iris_cy = local_cy + int(gaze_y) - int(geom.eye_half_h * 0.04)

            if self.iris_cutout_mask is not None:
                cw, ch = self.iris_cutout_mask.get_size()
                self.eye_box_canvas.blit(
                    self.iris_cutout_mask,
                    (iris_cx - cw // 2, iris_cy - ch // 2),
                    special_flags=pygame.BLEND_RGBA_MULT,
                )

            # Restrained atmospheric glow
            glow_surf = self.iris_layers.get("glow")
            if glow_surf is not None:
                gw, gh = glow_surf.get_size()
                glow_surf.set_alpha(int(95 + 30 * math.sin(now * 1.2)))
                self.eye_box_canvas.blit(
                    glow_surf,
                    (iris_cx - gw // 2, iris_cy - gh // 2),
                    special_flags=pygame.BLEND_RGBA_ADD,
                )

            # Concentric iris rings with slow color transition + ROTATING innermost rings
            iris_mix = 0.5 + 0.5 * math.sin(now * 0.60)
            rings_a = self.iris_layers.get("rings_a")
            rings_b = self.iris_layers.get("rings_b")
            if rings_a is not None and rings_b is not None:
                rw, rh = rings_a.get_size()
                rx, ry = iris_cx - rw // 2, iris_cy - rh // 2

                # Rotate the innermost rings (rings_b = phase-shifted colors) for living eye effect
                ring_rotation = now * 8.0  # degrees per second - gentle rotation
                rotated_rings_b = pygame.transform.rotate(rings_b, ring_rotation)
                rb_w, rb_h = rotated_rings_b.get_size()

                rings_a.set_alpha(255)
                self.eye_box_canvas.blit(rings_a, (rx, ry))
                rings_b.set_alpha(int(iris_mix * 255))
                self.eye_box_canvas.blit(rotated_rings_b, (iris_cx - rb_w // 2, iris_cy - rb_h // 2))

            # Radial iris spokes with subtle breathing + rotation
            rad_a = self.iris_layers.get("radial_a")
            rad_b = self.iris_layers.get("radial_b")
            if rad_a is not None and rad_b is not None:
                rw, rh = rad_a.get_size()
                r_scale = 1.0 + 0.025 * math.sin(now * 1.3)
                srw, srh = int(rw * r_scale), int(rh * r_scale)
                s_ra = pygame.transform.smoothscale(rad_a, (srw, srh))
                s_rb = pygame.transform.smoothscale(rad_b, (srw, srh))

                # Rotate radial spokes in opposite directions for depth
                radial_rot = now * 12.0  # degrees per second
                s_ra_rot = pygame.transform.rotate(s_ra, radial_rot)
                s_rb_rot = pygame.transform.rotate(s_rb, -radial_rot * 0.7)
                ra_w, ra_h = s_ra_rot.get_size()
                rb_w, rb_h = s_rb_rot.get_size()

                rx, ry = iris_cx - srw // 2, iris_cy - srh // 2
                s_ra.set_alpha(230)
                self.eye_box_canvas.blit(s_ra_rot, (iris_cx - ra_w // 2, iris_cy - ra_h // 2))
                s_rb.set_alpha(int(iris_mix * 230))
                self.eye_box_canvas.blit(s_rb_rot, (iris_cx - rb_w // 2, iris_cy - rb_h // 2))

            # Deep circular Pupil with subtle dilation/contraction + rotation
            pupil_surf = self.iris_layers.get("pupil")
            if pupil_surf is not None:
                pw, ph = pupil_surf.get_size()
                p_scale = 1.0 + 0.055 * math.sin(now * 0.92) + 0.035 * (1.0 - openness)
                spw, sph = int(pw * p_scale), int(ph * p_scale)
                s_pupil = pygame.transform.smoothscale(pupil_surf, (spw, sph))

                # Slow counter-rotation for pupil words
                pupil_rot = now * (-6.0)  # slow counter-clockwise
                s_pupil_rot = pygame.transform.rotate(s_pupil, pupil_rot)
                pp_w, pp_h = s_pupil_rot.get_size()
                self.eye_box_canvas.blit(
                    s_pupil_rot, (iris_cx - pp_w // 2, iris_cy - pp_h // 2)
                )

            # Crisp corneal highlight words
            hl_surf = self.iris_layers.get("highlights")
            if hl_surf is not None:
                hw, hh = hl_surf.get_size()
                hl_x = local_cx + int(gaze_x * 1.16) - hw // 2
                hl_y = local_cy + int(gaze_y * 1.16) - int(geom.eye_half_h * 0.04) - hh // 2
                self.eye_box_canvas.blit(hl_surf, (hl_x, hl_y))

            # Clip the eye interior to the instantaneous upper & lower eyelid curves!
            y_up, y_lo = eval_eyelid_curves(self.mask_u, openness, geom)
            lid_gaze_y = gaze_y * 0.20 * openness
            mask_x = local_cx + self.mask_u * geom.eye_half_w
            y_up_box = local_cy + y_up + lid_gaze_y
            y_lo_box = local_cy + y_lo + lid_gaze_y

            poly_pts = list(zip(mask_x.tolist(), y_up_box.tolist())) + list(
                zip(mask_x[::-1].tolist(), y_lo_box[::-1].tolist())
            )
            self.eye_box_mask.fill((0, 0, 0, 0))
            if len(poly_pts) >= 3:
                pygame.draw.polygon(self.eye_box_mask, (255, 255, 255, 140), poly_pts, width=4)
                pygame.draw.polygon(self.eye_box_mask, (255, 255, 255, 255), poly_pts, width=0)

            self.eye_box_canvas.blit(
                self.eye_box_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT
            )
            self.virtual_frame_surf.blit(self.eye_box_canvas, (bx, by))

        # 3. Render the single clean moving Upper & Lower Eyelid Rim stream along the eyelid margin
        if openness < 0.22:
            angle_idx = 0
        elif openness < 0.68:
            angle_idx = 1
        else:
            angle_idx = 2

        u_arr = np.array([w.u for w in self.eyelid_rim_words], dtype=np.float32)
        y_up_w, y_lo_w = eval_eyelid_curves(u_arr, openness, geom)
        lid_gaze_y = gaze_y * 0.20 * openness

        for idx, w in enumerate(self.eyelid_rim_words):
            surf = w.surfaces[angle_idx]
            wx = geom.center_x + w.u * geom.eye_half_w
            base_y = float(y_up_w[idx]) if w.is_upper else float(y_lo_w[idx])
            wy = geom.center_y + base_y + lid_gaze_y + w.v_offset
            sw, sh_h = surf.get_size()
            self.virtual_frame_surf.blit(surf, (int(wx) - sw // 2, int(wy) - sh_h // 2))

        # 4. Camera Zoom Transformation: crop `cam_rect` from `virtual_frame_surf`
        #    and smoothly scale to the physical MacBook screen resolution
        sub_view = self.virtual_frame_surf.subsurface(cam_rect)
        pygame.transform.smoothscale(
            sub_view, (geom.screen_w, geom.screen_h), self.screen
        )

    def _render_help_overlay(self) -> None:
        if not self.show_help:
            return
        palette = PALETTES[self.palette_idx]
        s = min(self.geom.screen_w / 1512.0, self.geom.screen_h / 982.0)
        panel_w = int(450 * s)
        panel_h = int(275 * s)
        pil_panel = Image.new("RGBA", (panel_w, panel_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(pil_panel)
        draw.rounded_rectangle(
            (0, 0, panel_w - 1, panel_h - 1),
            radius=int(12 * s),
            fill=(6, 10, 18, 230),
            outline=(*palette.accent_tint, 160),
            width=1,
        )

        title_font = self.font_mgr.get_font(int(16 * s), bold=True)
        body_font = self.font_mgr.get_font(int(13 * s), bold=False)

        lines = [
            ("THE EYE WITHIN WORDS — Controls", True),
            (f"Palette: {palette.name}", False),
            (
                f"Zoom: {self.camera.zoom:.2f}x ({'AUTO' if self.camera.auto_zoom else 'LOCKED'})  |  Blink: {'AUTO' if self.blink_ctrl.auto_blink else 'MANUAL'}  |  FPS: {int(self.clock.get_fps())}",
                False,
            ),
            ("", False),
            ("SPACE : Trigger an immediate blink", False),
            ("B     : Enable / disable automatic blinking", False),
            ("Z     : Toggle automatic camera zooming", False),
            ("C     : Change the color palette", False),
            ("R     : Regenerate arrangement of quotes", False),
            ("H     : Show / hide keyboard instructions", False),
            ("ESC   : Close the animation safely", False),
        ]

        y_cursor = int(16 * s)
        for text, is_header in lines:
            if not text:
                y_cursor += int(6 * s)
                continue
            font = title_font if is_header else body_font
            col = (240, 248, 255, 255) if is_header else (180, 206, 232, 240)
            draw.text((int(20 * s), y_cursor), text, font=font, fill=col)
            y_cursor += int((24 if is_header else 20) * s)

        self.screen.blit(pil_to_pygame(pil_panel), (int(28 * s), int(28 * s)))

    def run(self) -> None:
        running = True
        frame_idx = 0
        prev_time = time.perf_counter()

        while running:
            now = time.perf_counter()
            dt = min(0.05, max(0.001, now - prev_time))
            prev_time = now

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    if self.windowed:
                        self.screen = pygame.display.set_mode(
                            (event.w, event.h), pygame.RESIZABLE | pygame.DOUBLEBUF
                        )
                        self._build_all_layers()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        self.blink_ctrl.trigger_blink(now, allow_double=False)
                    elif event.key == pygame.K_b:
                        self.blink_ctrl.auto_blink = not self.blink_ctrl.auto_blink
                    elif event.key == pygame.K_z:
                        self.camera.auto_zoom = not self.camera.auto_zoom
                    elif event.key == pygame.K_c:
                        self.palette_idx = (self.palette_idx + 1) % len(PALETTES)
                        self._build_all_layers()
                    elif event.key == pygame.K_r:
                        self.seed = random.randint(10000, 999999)
                        self._build_all_layers()
                    elif event.key == pygame.K_h:
                        self.show_help = not self.show_help

            openness = self.blink_ctrl.update(now)
            override_zoom: Optional[float] = None

            if self.test_frames > 0 and self.screenshot_dir:
                if frame_idx == 8:
                    openness = 1.0
                    override_zoom = 1.0
                elif frame_idx == 20:
                    openness = 1.0
                    override_zoom = 2.35
                elif frame_idx == 32:
                    openness = 0.0
                    override_zoom = 1.12

            cam_rect, gaze_x, gaze_y = self.camera.manage_zoom_and_camera(
                self.geom, now, dt, override_zoom=override_zoom
            )
            self.render_fullscreen_composition(openness, cam_rect, gaze_x, gaze_y, now)
            self._render_help_overlay()

            pygame.display.flip()
            self.clock.tick(60)

            if self.test_frames > 0 and self.screenshot_dir:
                if frame_idx in (8, 20, 32):
                    label = {8: "wide_open", 20: "closeup_zoom", 32: "blink_closed"}[frame_idx]
                    out_path = os.path.join(self.screenshot_dir, f"eye_within_words_{label}.png")
                    raw_rgb = pygame.image.tostring(self.screen, "RGB")
                    Image.frombytes("RGB", self.screen.get_size(), raw_rgb).save(out_path)
                if frame_idx >= self.test_frames:
                    running = False

            frame_idx += 1

        pygame.quit()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="THE EYE WITHIN WORDS — Python Generative Typography Animation"
    )
    parser.add_argument(
        "--windowed",
        action="store_true",
        help="Run in a resizable window instead of macOS full-screen mode.",
    )
    parser.add_argument(
        "--test-frames",
        type=int,
        default=0,
        help="Run for N frames and exit automatically (for visual verification).",
    )
    parser.add_argument(
        "--screenshot-dir",
        type=str,
        default=None,
        help="Directory to save verification screenshots when --test-frames is used.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    app = EyeWithinWordsApp(
        windowed=args.windowed,
        test_frames=args.test_frames,
        screenshot_dir=args.screenshot_dir,
    )
    app.run()
