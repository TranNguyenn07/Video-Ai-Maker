import json
import math
import os
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


# ============================================================
# AI VIDEO MAKER - RENDER ONLY
# ------------------------------------------------------------
# This file intentionally DOES NOT call FFmpeg.
# It creates exactly:
#   frame1.png ... frame12.png
# in the repository root.
#
# Video creation is handled by .github/workflows/video.yml.
# ============================================================

WIDTH = 1080
HEIGHT = 1920

TOTAL_SECONDS = 60
SCENE_COUNT = 12
SCENE_SECONDS = TOTAL_SECONDS / SCENE_COUNT

BASE_DIR = Path(__file__).resolve().parent
CHAR_JSON = BASE_DIR / "char.json"

# The workflow expects the frames in the repository root.
FRAME_DIR = BASE_DIR

# Keep a second copy for inspection/artifacts.
OUTPUT_DIR = BASE_DIR / "output" / "frames"

VIDEO_PROMPT = (
    os.environ.get("VIDEO_PROMPT", "").strip()
    or os.environ.get("INPUT_PROMPT", "").strip()
    or (
        "Miu và Bống tìm thấy một chú chim non bị lạc trong khu rừng "
        "và cùng nhau giúp chú chim trở về với mẹ."
    )
)


# ============================================================
# EXACT CHARACTER DATA
# ------------------------------------------------------------
# char.json is read when present so the project keeps one
# character source of truth. The renderer never asks an AI to
# invent/restyle these characters.
# ============================================================

CHARACTER_FALLBACK = {
    "CHAR_01": {
        "name": "Miu",
        "description": (
            "Miu, a small round fox kit with bright orange fur, a pure "
            "white belly and white-tipped tail, big round expressive eyes, "
            "large fluffy ears with white fur tips, two small white fur "
            "streaks on both cheeks, wearing a pastel sky-blue scarf with "
            "small white polka dots tied around the neck. Child-like "
            "proportions, 3D animated movie style, extremely cute and "
            "expressive. This exact character design must be used."
        ),
    },
    "CHAR_02": {
        "name": "Bống",
        "description": (
            "Bống, a small rabbit kit with cream-white fur, long upright "
            "ears with pale pink inner ears, the left ear slightly drooping, "
            "wearing a pale butter-yellow overall, with a small pale pink "
            "flower tucked behind the left ear. Child-like proportions, "
            "3D animated movie style, soft and gentle design. This exact "
            "character design must be used."
        ),
    },
}


def load_characters():
    """
    Load character definitions from char.json if available.

    Supported forms:
      {
        "CHAR_01": {...},
        "CHAR_02": {...}
      }

    or:
      {
        "characters": {
          "CHAR_01": {...},
          "CHAR_02": {...}
        }
      }

    If char.json is absent or malformed, the exact built-in definitions
    above are used so rendering remains deterministic.
    """
    if not CHAR_JSON.exists():
        return CHARACTER_FALLBACK.copy()

    try:
        data = json.loads(CHAR_JSON.read_text(encoding="utf-8"))

        if isinstance(data, dict) and isinstance(
            data.get("characters"), dict
        ):
            data = data["characters"]

        if not isinstance(data, dict):
            raise ValueError("char.json must contain a JSON object")

        result = {}

        for key in ("CHAR_01", "CHAR_02"):
            value = data.get(key)

            if isinstance(value, dict):
                fallback = CHARACTER_FALLBACK[key].copy()
                fallback.update(value)
                result[key] = fallback
            else:
                result[key] = CHARACTER_FALLBACK[key].copy()

        return result

    except Exception as exc:
        print(
            f"WARNING: Could not read char.json: {exc}",
            file=sys.stderr,
        )
        print("Using exact built-in character definitions.")


        return CHARACTER_FALLBACK.copy()


CHARACTERS = load_characters()


# ============================================================
# FONTS
# ============================================================

def get_font(size, bold=False):
    candidates = []

    if bold:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        ]
    else:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        ]

    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)

    return ImageFont.load_default()


FONT_SCENE = get_font(54, True)
FONT_TEXT = get_font(37, False)
FONT_SMALL = get_font(28, False)


# ============================================================
# STORY
# ============================================================

def make_story(topic):
    """
    Deterministic 12-scene story.

    No external AI API is called.
    """

    return [
        (
            "Buổi sáng trong khu rừng nhỏ, Miu và Bống đang vui chơi "
            f"thì phát hiện ra rằng {topic}"
        ),
        (
            "Miu nhìn quanh khu rừng thật kỹ và nhận ra có điều gì "
            "đó không ổn."
        ),
        (
            "Bống bước lại gần Miu và hỏi xem hai người bạn có thể "
            "làm gì để giúp đỡ."
        ),
        (
            "Miu lắng nghe thật chăm chú và nghe thấy một âm thanh "
            "rất nhỏ ở phía xa."
        ),
        (
            "Hai người bạn quyết định đi theo con đường nhỏ xuyên "
            "qua khu rừng."
        ),
        (
            "Bống phát hiện một vài dấu vết bé xíu trên mặt đất "
            "phủ đầy lá."
        ),
        (
            "Hai người bạn gặp một chú chim non nhỏ đang lo lắng "
            "vì không thể tìm thấy mẹ."
        ),
        (
            "Miu nhẹ nhàng an ủi chú chim, còn Bống nhìn quanh để "
            "tìm dấu hiệu của chim mẹ."
        ),
        (
            "Hai người bạn cùng đưa chú chim non đến gần một cái "
            "cây lớn và tìm thấy chiếc tổ."
        ),
        (
            "Từ trên cao, một tiếng chim quen thuộc vang lên và "
            "chú chim non vui mừng khi nhìn thấy mẹ."
        ),
        (
            "Miu và Bống mỉm cười vì đã giúp được một người bạn "
            "nhỏ trở về với gia đình."
        ),
        (
            "Hai người bạn cùng trở về nhà và hiểu rằng một việc "
            "tốt dù nhỏ cũng có thể làm một ngày trở nên thật đẹp."
        ),
    ]


# ============================================================
# TEXT WRAP
# ============================================================

def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""

    for word in words:
        candidate = word if not current else current + " " + word

        bbox = draw.textbbox(
            (0, 0),
            candidate,
            font=font,
        )

        width = bbox[2] - bbox[0]

        if width <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)

            current = word

    if current:
        lines.append(current)

    return lines


# ============================================================
# DRAW HELPERS
# ============================================================

def gradient_background(draw, top, bottom):
    for y in range(HEIGHT):
        t = y / float(HEIGHT - 1)

        color = tuple(
            int(top[i] + (bottom[i] - top[i]) * t)
            for i in range(3)
        )

        draw.line(
            (0, y, WIDTH, y),
            fill=color,
        )


def draw_cloud(draw, x, y, scale=1.0):
    color = (250, 253, 255)

    for dx, dy, radius in [
        (-80, 15, 55),
        (0, -15, 75),
        (80, 15, 55),
    ]:
        cx = int(x + dx * scale)
        cy = int(y + dy * scale)
        r = int(radius * scale)

        draw.ellipse(
            (
                cx - r,
                cy - r,
                cx + r,
                cy + r,
            ),
            fill=color,
        )


def draw_tree(draw, x, y, scale=1.0):
    trunk_w = int(60 * scale)
    trunk_h = int(270 * scale)

    draw.rounded_rectangle(
        (
            x - trunk_w // 2,
            y,
            x + trunk_w // 2,
            y + trunk_h,
        ),
        radius=max(1, int(18 * scale)),
        fill=(110, 75, 48),
    )

    for dx, dy, radius in [
        (-90, -30, 100),
        (0, -90, 125),
        (95, -20, 95),
        (20, 20, 105),
    ]:
        cx = int(x + dx * scale)
        cy = int(y + dy * scale)
        r = int(radius * scale)

        draw.ellipse(
            (
                cx - r,
                cy - r,
                cx + r,
                cy + r,
            ),
            fill=(84, 154, 91),
        )


def draw_bird(draw, x, y, scale=1.0):
    body = (221, 170, 86)
    wing = (194, 139, 65)
    dark = (40, 35, 30)
    beak = (230, 165, 58)

    rx = int(48 * scale)
    ry = int(35 * scale)

    draw.ellipse(
        (
            x - rx,
            y - ry,
            x + rx,
            y + ry,
        ),
        fill=body,
    )

    draw.ellipse(
        (
            x - int(5 * scale),
            y - int(10 * scale),
            x + int(45 * scale),
            y + int(25 * scale),
        ),
        fill=wing,
    )

    eye_r = max(2, int(6 * scale))
    eye_x = x + int(18 * scale)
    eye_y = y - int(15 * scale)

    draw.ellipse(
        (
            eye_x - eye_r,
            eye_y - eye_r,
            eye_x + eye_r,
            eye_y + eye_r,
        ),
        fill=dark,
    )

    draw.polygon(
        [
            (
                x + int(47 * scale),
                y,
            ),
            (
                x + int(75 * scale),
                y + int(9 * scale),
            ),
            (
                x + int(47 * scale),
                y + int(18 * scale),
            ),
        ],
        fill=beak,
    )


# ============================================================
# MIU - EXACT DESIGN
# ============================================================

def draw_miu(draw, cx, cy, scale=1.0, emotion="happy"):
    orange = (239, 119, 47)
    orange_light = (255, 145, 60)
    white = (255, 250, 242)
    dark = (55, 38, 32)

    scarf = (151, 205, 230)
    scarf_dot = (248, 252, 255)

    # Ground shadow
    draw.ellipse(
        (
            cx - int(170 * scale),
            cy + int(260 * scale),
            cx + int(170 * scale),
            cy + int(320 * scale),
        ),
        fill=(50, 60, 50),
    )

    # White-tipped tail
    tx = cx + int(150 * scale)
    ty = cy + int(145 * scale)

    draw.ellipse(
        (
            tx - int(120 * scale),
            ty - int(80 * scale),
            tx + int(100 * scale),
            ty + int(100 * scale),
        ),
        fill=orange_light,
    )

    draw.ellipse(
        (
            tx + int(35 * scale),
            ty - int(30 * scale),
            tx + int(105 * scale),
            ty + int(85 * scale),
        ),
        fill=white,
    )

    # Round body
    draw.ellipse(
        (
            cx - int(150 * scale),
            cy - int(30 * scale),
            cx + int(150 * scale),
            cy + int(290 * scale),
        ),
        fill=orange,
    )

    # Pure white belly
    draw.ellipse(
        (
            cx - int(92 * scale),
            cy + int(70 * scale),
            cx + int(92 * scale),
            cy + int(255 * scale),
        ),
        fill=white,
    )

    # Large fluffy ears
    draw.polygon(
        [
            (
                cx - int(115 * scale),
                cy - int(80 * scale),
            ),
            (
                cx - int(150 * scale),
                cy - int(260 * scale),
            ),
            (
                cx - int(35 * scale),
                cy - int(165 * scale),
            ),
        ],
        fill=orange,
    )

    draw.polygon(
        [
            (
                cx + int(35 * scale),
                cy - int(165 * scale),
            ),
            (
                cx + int(150 * scale),
                cy - int(260 * scale),
            ),
            (
                cx + int(115 * scale),
                cy - int(80 * scale),
            ),
        ],
        fill=orange,
    )

    # White ear tips
    draw.polygon(
        [
            (
                cx - int(105 * scale),
                cy - int(125 * scale),
            ),
            (
                cx - int(130 * scale),
                cy - int(225 * scale),
            ),
            (
                cx - int(55 * scale),
                cy - int(165 * scale),
            ),
        ],
        fill=white,
    )

    draw.polygon(
        [
            (
                cx + int(55 * scale),
                cy - int(165 * scale),
            ),
            (
                cx + int(130 * scale),
                cy - int(225 * scale),
            ),
            (
                cx + int(105 * scale),
                cy - int(125 * scale),
            ),
        ],
        fill=white,
    )

    # Head
    draw.ellipse(
        (
            cx - int(160 * scale),
            cy - int(175 * scale),
            cx + int(160 * scale),
            cy + int(120 * scale),
        ),
        fill=orange_light,
    )

    # Two white cheek streaks
    draw.rounded_rectangle(
        (
            cx - int(118 * scale),
            cy + int(10 * scale),
            cx - int(72 * scale),
            cy + int(24 * scale),
        ),
        radius=max(2, int(7 * scale)),
        fill=white,
    )

    draw.rounded_rectangle(
        (
            cx + int(72 * scale),
            cy + int(10 * scale),
            cx + int(118 * scale),
            cy + int(24 * scale),
        ),
        radius=max(2, int(7 * scale)),
        fill=white,
    )

    # Large expressive eyes
    eye_y = cy - int(60 * scale)

    for ex in (
        cx - int(62 * scale),
        cx + int(62 * scale),
    ):
        r = int(39 * scale)

        draw.ellipse(
            (
                ex - r,
                eye_y - r,
                ex + r,
                eye_y + r,
            ),
            fill=white,
        )

        r2 = int(22 * scale)

        draw.ellipse(
            (
                ex - r2,
                eye_y - r2,
                ex + r2,
                eye_y + r2,
            ),
            fill=dark,
        )

        draw.ellipse(
            (
                ex - int(8 * scale),
                eye_y - int(12 * scale),
                ex + int(4 * scale),
                eye_y,
            ),
            fill=white,
        )

    # Nose
    draw.ellipse(
        (
            cx - int(28 * scale),
            cy,
            cx + int(28 * scale),
            cy + int(38 * scale),
        ),
        fill=(90, 58, 48),
    )

    # Mouth
    if emotion == "sad":
        start_angle = 200
        end_angle = 340
    else:
        start_angle = 20
        end_angle = 160

    draw.arc(
        (
            cx - int(35 * scale),
            cy + int(15 * scale),
            cx + int(35 * scale),
            cy + int(75 * scale),
        ),
        start_angle,
        end_angle,
        fill=dark,
        width=max(2, int(5 * scale)),
    )

    # Pastel sky-blue scarf
    draw.rounded_rectangle(
        (
            cx - int(125 * scale),
            cy + int(100 * scale),
            cx + int(125 * scale),
            cy + int(155 * scale),
        ),
        radius=max(1, int(25 * scale)),
        fill=scarf,
    )

    # Small white polka dots
    for dx in (-75, -25, 25, 75):
        r = max(2, int(6 * scale))
        x = cx + int(dx * scale)
        y = cy + int(120 * scale)

        draw.ellipse(
            (
                x - r,
                y - r,
                x + r,
                y + r,
            ),
            fill=scarf_dot,
        )


# ============================================================
# BỐNG - EXACT DESIGN
# ============================================================

def draw_bong(draw, cx, cy, scale=1.0):
    cream = (247, 244, 226)
    white = (255, 250, 237)
    pink = (241, 177, 188)
    yellow = (239, 218, 132)
    dark = (62, 54, 48)

    # Ground shadow
    draw.ellipse(
        (
            cx - int(160 * scale),
            cy + int(265 * scale),
            cx + int(160 * scale),
            cy + int(320 * scale),
        ),
        fill=(50, 60, 50),
    )

    # Body
    draw.ellipse(
        (
            cx - int(145 * scale),
            cy,
            cx + int(145 * scale),
            cy + int(290 * scale),
        ),
        fill=cream,
    )

    # Pale butter-yellow overall
    draw.rounded_rectangle(
        (
            cx - int(115 * scale),
            cy + int(100 * scale),
            cx + int(115 * scale),
            cy + int(300 * scale),
        ),
        radius=max(1, int(40 * scale)),
        fill=yellow,
    )

    # Left ear: slightly drooping
    draw.polygon(
        [
            (
                cx - int(135 * scale),
                cy - int(80 * scale),
            ),
            (
                cx - int(175 * scale),
                cy - int(255 * scale),
            ),
            (
                cx - int(35 * scale),
                cy - int(155 * scale),
            ),
        ],
        fill=white,
    )

    # Right ear: upright
    draw.rounded_rectangle(
        (
            cx + int(35 * scale),
            cy - int(280 * scale),
            cx + int(135 * scale),
            cy - int(30 * scale),
        ),
        radius=max(1, int(45 * scale)),
        fill=white,
    )

    # Pale pink inner ears
    draw.polygon(
        [
            (
                cx - int(115 * scale),
                cy - int(110 * scale),
            ),
            (
                cx - int(145 * scale),
                cy - int(215 * scale),
            ),
            (
                cx - int(58 * scale),
                cy - int(155 * scale),
            ),
        ],
        fill=pink,
    )

    draw.rounded_rectangle(
        (
            cx + int(58 * scale),
            cy - int(255 * scale),
            cx + int(112 * scale),
            cy - int(60 * scale),
        ),
        radius=max(1, int(27 * scale)),
        fill=pink,
    )

    # Head
    draw.ellipse(
        (
            cx - int(160 * scale),
            cy - int(180 * scale),
            cx + int(160 * scale),
            cy + int(115 * scale),
        ),
        fill=white,
    )

    # Eyes
    eye_y = cy - int(62 * scale)

    for ex in (
        cx - int(62 * scale),
        cx + int(62 * scale),
    ):
        r = int(37 * scale)

        draw.ellipse(
            (
                ex - r,
                eye_y - r,
                ex + r,
                eye_y + r,
            ),
            fill=white,
        )

        r2 = int(20 * scale)

        draw.ellipse(
            (
                ex - r2,
                eye_y - r2,
                ex + r2,
                eye_y + r2,
            ),
            fill=dark,
        )

        draw.ellipse(
            (
                ex - int(7 * scale),
                eye_y - int(11 * scale),
                ex + int(3 * scale),
                eye_y,
            ),
            fill=white,
        )

    # Nose
    draw.ellipse(
        (
            cx - int(18 * scale),
            cy,
            cx + int(18 * scale),
            cy + int(25 * scale),
        ),
        fill=pink,
    )

    # Mouth
    draw.arc(
        (
            cx - int(35 * scale),
            cy + int(12 * scale),
            cx + int(35 * scale),
            cy + int(62 * scale),
        ),
        20,
        160,
        fill=dark,
        width=max(2, int(5 * scale)),
    )

    # Small pale pink flower behind left ear
    fx = cx - int(135 * scale)
    fy = cy - int(175 * scale)

    for angle in range(0, 360, 72):
        rad = math.radians(angle)

        px = fx + int(math.cos(rad) * 22 * scale)
        py = fy + int(math.sin(rad) * 22 * scale)

        r = int(15 * scale)

        draw.ellipse(
            (
                px - r,
                py - r,
                px + r,
                py + r,
            ),
            fill=pink,
        )

    r = int(10 * scale)

    draw.ellipse(
        (
            fx - r,
            fy - r,
            fx + r,
            fy + r,
        ),
        fill=(244, 196, 77),
    )


# ============================================================
# SCENE
# ============================================================

def draw_scene(index, text):
    random.seed(1000 + index)

    image = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        (220, 240, 220),
    )

    draw = ImageDraw.Draw(image)

    palettes = [
        ((170, 220, 247), (238, 250, 222)),
        ((190, 225, 250), (239, 247, 219)),
        ((155, 205, 240), (230, 244, 210)),
        ((205, 230, 247), (246, 238, 205)),
    ]

    top, bottom = palettes[index % len(palettes)]

    gradient_background(
        draw,
        top,
        bottom,
    )

    # Sun
    draw.ellipse(
        (760, 120, 960, 320),
        fill=(255, 232, 139),
    )

    # Clouds
    draw_cloud(
        draw,
        210,
        280,
        0.9,
    )

    draw_cloud(
        draw,
        820,
        430,
        0.65,
    )

    # Distant hills
    draw.polygon(
        [
            (0, 1000),
            (180, 850),
            (360, 980),
            (550, 820),
            (760, 970),
            (930, 830),
            (1080, 970),
            (1080, 1300),
            (0, 1300),
        ],
        fill=(126, 181, 122),
    )

    # Ground
    draw.rectangle(
        (0, 1200, WIDTH, HEIGHT),
        fill=(133, 184, 104),
    )

    # Path
    draw.polygon(
        [
            (420, HEIGHT),
            (660, HEIGHT),
            (585, 1190),
            (495, 1190),
        ],
        fill=(218, 190, 142),
    )

    # Trees
    draw_tree(
        draw,
        130,
        820,
        0.95,
    )

    draw_tree(
        draw,
        930,
        850,
        0.85,
    )

    if index % 3 == 0:
        draw_tree(
            draw,
            530,
            900,
            0.65,
        )

    # Flowers
    for _ in range(25):
        x = random.randint(
            20,
            WIDTH - 20,
        )

        y = random.randint(
            1260,
            HEIGHT - 80,
        )

        r = random.randint(
            3,
            7,
        )

        draw.ellipse(
            (
                x - r,
                y - r,
                x + r,
                y + r,
            ),
            fill=(255, 245, 210),
        )

    # Character positions
    positions = [
        (380, 1060, 690, 1080),
        (330, 1050, 720, 1080),
        (420, 1070, 760, 1080),
        (360, 1060, 690, 1090),
    ]

    miu_x, miu_y, bong_x, bong_y = positions[
        index % len(positions)
    ]

    # Story progression
    emotion = "sad" if index in (6, 7, 8) else "happy"

    draw_miu(
        draw,
        miu_x,
        miu_y,
        1.0,
        emotion,
    )

    draw_bong(
        draw,
        bong_x,
        bong_y,
        0.92,
    )

    # Bird appears from scene 7 onward.
    if index >= 6:
        draw_bird(
            draw,
            790,
            970,
            0.75,
        )

    # Nest appears during rescue/reunion.
    if index >= 7:
        draw.ellipse(
            (770, 990, 980, 1070),
            fill=(125, 86, 50),
        )

        draw.ellipse(
            (800, 1000, 950, 1050),
            fill=(235, 216, 165),
        )

    # Scene number
    draw.text(
        (65, 55),
        f"{index + 1:02d}/{SCENE_COUNT:02d}",
        font=FONT_SCENE,
        fill=(255, 255, 255),
    )

    # Vietnamese subtitle card
    card_x1 = 55
    card_y1 = HEIGHT - 390
    card_x2 = WIDTH - 55
    card_y2 = HEIGHT - 55

    draw.rounded_rectangle(
        (
            card_x1,
            card_y1,
            card_x2,
            card_y2,
        ),
        radius=35,
        fill=(255, 255, 255),
    )

    lines = wrap_text(
        draw,
        text,
        FONT_TEXT,
        (card_x2 - card_x1) - 70,
    )

    line_height = 50
    total_height = len(lines) * line_height

    y = (
        card_y1
        + (
            (card_y2 - card_y1)
            - total_height
        ) // 2
    )

    for line in lines:
        bbox = draw.textbbox(
            (0, 0),
            line,
            font=FONT_TEXT,
        )

        text_width = bbox[2] - bbox[0]
        x = (WIDTH - text_width) // 2

        draw.text(
            (x, y),
            line,
            font=FONT_TEXT,
            fill=(45, 45, 45),
        )

        y += line_height

    # Duration marker
    duration_text = f"{SCENE_SECONDS:.1f}s"

    draw.text(
        (WIDTH - 160, 65),
        duration_text,
        font=FONT_SMALL,
        fill=(255, 255, 255),
    )

    return image


# ============================================================
# FILE VALIDATION
# ============================================================

def validate_png(path):
    if not path.is_file():
        raise RuntimeError(
            f"Missing generated frame: {path.name}"
        )

    if path.stat().st_size <= 100:
        raise RuntimeError(
            f"Generated frame is too small: {path.name}"
        )

    try:
        with Image.open(path) as img:
            img.verify()

        with Image.open(path) as img:
            if img.format != "PNG":
                raise RuntimeError(
                    f"Not a PNG: {path.name}"
                )

            if img.size != (WIDTH, HEIGHT):
                raise RuntimeError(
                    f"Wrong dimensions for {path.name}: "
                    f"{img.size}, expected {(WIDTH, HEIGHT)}"
                )

    except Exception as exc:
        raise RuntimeError(
            f"Invalid PNG {path.name}: {exc}"
        ) from exc


def atomic_save_png(image, target):
    temp = target.with_name(
        target.name + ".tmp.png"
    )

    try:
        image.save(
            temp,
            format="PNG",
            optimize=True,
        )

        validate_png(temp)

        temp.replace(target)

    finally:
        if temp.exists():
            temp.unlink()


# ============================================================
# CLEAN
# ============================================================

def clean_old_frames():
    """
    Remove only frame1.png ... frame12.png.

    This prevents stale frames from previous workflow runs
    from being accidentally used.
    """

    for i in range(1, SCENE_COUNT + 1):
        root_path = FRAME_DIR / f"frame{i}.png"
        output_path = OUTPUT_DIR / f"frame{i}.png"

        if root_path.exists():
            root_path.unlink()

        if output_path.exists():
            output_path.unlink()

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


# ============================================================
# RENDER
# ============================================================

def render():
    print("=" * 60)
    print("START RENDER")
    print("=" * 60)

    print(f"Resolution : {WIDTH}x{HEIGHT}")
    print(f"Duration   : {TOTAL_SECONDS} seconds")
    print(f"Scenes     : {SCENE_COUNT}")
    print(f"Scene time : {SCENE_SECONDS:.2f} seconds")
    print("Audio      : none")
    print("Music      : none")
    print("Image API  : none")
    print("FFmpeg     : not used by render.py")

    print("=" * 60)

    clean_old_frames()

    story = make_story(
        VIDEO_PROMPT
    )

    if len(story) != SCENE_COUNT:
        raise RuntimeError(
            f"Internal story error: got {len(story)} scenes, "
            f"expected exactly {SCENE_COUNT}."
        )

    generated = []

    for index, text in enumerate(
        story,
        start=1,
    ):
        print(
            f"[{index:02d}/{SCENE_COUNT:02d}] "
            f"Creating frame{index}.png ..."
        )

        image = draw_scene(
            index - 1,
            text,
        )

        root_path = (
            FRAME_DIR
            / f"frame{index}.png"
        )

        output_path = (
            OUTPUT_DIR
            / f"frame{index}.png"
        )

        # Save finished image to both locations.
        atomic_save_png(
            image,
            root_path,
        )

        atomic_save_png(
            image,
            output_path,
        )

        # Validate immediately.
        validate_png(root_path)
        validate_png(output_path)

        generated.append(root_path)

        print(
            f"[{index:02d}/{SCENE_COUNT:02d}] "
            f"OK frame{index}.png "
            f"({root_path.stat().st_size} bytes)"
        )

    # ========================================================
    # FINAL STRICT CHECK
    # ========================================================

    expected = [
        FRAME_DIR / f"frame{i}.png"
        for i in range(
            1,
            SCENE_COUNT + 1,
        )
    ]

    missing = [
        path.name
        for path in expected
        if not path.is_file()
    ]

    if missing:
        raise RuntimeError(
            f"Render finished with missing frames: {missing}"
        )

    root_pngs = sorted(
        FRAME_DIR.glob("frame*.png"),
        key=lambda p: p.name,
    )

    if len(root_pngs) != SCENE_COUNT:
        raise RuntimeError(
            f"Root frame count is {len(root_pngs)}, "
            f"expected exactly {SCENE_COUNT}."
        )

    for path in expected:
        validate_png(path)

    # ========================================================
    # MANIFEST
    # ========================================================

    manifest = {
        "width": WIDTH,
        "height": HEIGHT,
        "total_seconds": TOTAL_SECONDS,
        "scene_count": SCENE_COUNT,
        "scene_seconds": SCENE_SECONDS,
        "frames": [
            path.name
            for path in expected
        ],
        "audio": False,
        "background_music": False,
        "image_api": False,
        "ffmpeg_in_render": False,
        "prompt": VIDEO_PROMPT,
        "characters": {
            key: {
                "name": value.get(
                    "name",
                    "",
                ),
                "description": value.get(
                    "description",
                    "",
                ),
            }
            for key, value in CHARACTERS.items()
        },
    }

    manifest_path = (
        BASE_DIR
        / "render_manifest.json"
    )

    manifest_path.write_text(
        json.dumps(
            manifest,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("=" * 60)
    print("RENDER SUCCESS")
    print("=" * 60)
    print(
        f"Exactly {SCENE_COUNT} valid PNG frames created."
    )
    print(
        "frame1.png ... frame12.png are ready "
        "for video.yml."
    )
    print("=" * 60)


# ============================================================
# MAIN
# ============================================================

def main():
    try:
        render()

    except KeyboardInterrupt:
        print(
            "Render cancelled."
        )
        raise SystemExit(130)

    except Exception as exc:
        print(
            f"ERROR: {exc}",
            file=sys.stderr,
        )
        raise SystemExit(1)


if __name__ == "__main__":
    main()
