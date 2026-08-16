import os
import sys
import json
import math
import random
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter


# ============================================================
# VIDEO AI MAKER
# FREE RENDER - KHÔNG DÙNG FLUX / HUGGING FACE IMAGE API
# ============================================================

WIDTH = 1080
HEIGHT = 1920

TOTAL_SECONDS = 60
SCENE_COUNT = 24
SCENE_SECONDS = TOTAL_SECONDS / SCENE_COUNT
FPS = 24

BASE_DIR = Path(__file__).resolve().parent
OUT = BASE_DIR / "output"
FRAMES = OUT / "frames"

OUT.mkdir(parents=True, exist_ok=True)
FRAMES.mkdir(parents=True, exist_ok=True)


# ============================================================
# CHARACTERS
# ============================================================

CHARACTERS = {
    "CHAR_01": {
        "name": "Miu",
        "description": (
            "Miu, a small round fox kit with bright orange fur, "
            "a pure white belly and white-tipped tail, big round "
            "expressive eyes, large fluffy ears with white fur tips, "
            "two small white fur streaks on both cheeks, wearing a "
            "pastel sky-blue scarf with small white polka dots tied "
            "around the neck. Child-like proportions, extremely cute "
            "and expressive. This exact character design must be used."
        ),
    },

    "CHAR_02": {
        "name": "Bống",
        "description": (
            "Bống, a small rabbit kit with cream-white fur, "
            "long upright ears with pale pink inner ears, the left "
            "ear slightly drooping, wearing a pale butter-yellow "
            "overall, with a small pale pink flower tucked behind "
            "the left ear. Child-like proportions, soft and gentle "
            "design. This exact character design must be used."
        ),
    },
}


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


FONT_TITLE = get_font(54, True)
FONT_SUBTITLE = get_font(37, False)
FONT_SMALL = get_font(28, False)


# ============================================================
# INPUT
# ============================================================

def get_prompt():
    """
    Nhận chủ đề từ:
    1. command line
    2. VIDEO_PROMPT
    3. INPUT_PROMPT
    4. giá trị mặc định
    """

    if len(sys.argv) > 1:
        value = sys.argv[1].strip()
        if value:
            return value

    value = os.environ.get("VIDEO_PROMPT", "").strip()
    if value:
        return value

    value = os.environ.get("INPUT_PROMPT", "").strip()
    if value:
        return value

    return (
        "Miu và Bống tìm thấy một chú chim non bị lạc "
        "trong khu rừng và cùng nhau giúp chú chim trở về với mẹ."
    )


# ============================================================
# STORY
# ============================================================

def make_story(topic):
    """
    Không gọi AI API.
    Tạo 24 cảnh từ chủ đề người dùng nhập.
    """

    return [
        f"Buổi sáng trong khu rừng nhỏ, Miu và Bống đang vui chơi thì phát hiện ra rằng {topic}",

        "Miu nhìn quanh khu rừng thật kỹ và nhận ra có điều gì đó không ổn.",

        "Bống bước lại gần Miu và hỏi xem hai người bạn có thể làm gì để giúp đỡ.",

        "Miu lắng nghe thật chăm chú và nghe thấy một âm thanh rất nhỏ ở phía xa.",

        "Hai người bạn quyết định đi theo con đường nhỏ xuyên qua khu rừng.",

        "Bống phát hiện một vài dấu vết bé xíu trên mặt đất phủ đầy lá.",

        "Miu và Bống cùng nhau đi theo những dấu vết ấy.",

        "Ánh nắng xuyên qua những tán cây khiến con đường phía trước trở nên thật ấm áp.",

        "Hai người bạn gặp một đoạn đường bị những cành cây nhỏ chắn ngang.",

        "Miu cẩn thận kéo những cành cây sang một bên.",

        "Bống cũng giúp Miu dọn đường để cả hai có thể tiếp tục đi.",

        "Đột nhiên, hai người bạn nghe thấy một tiếng gọi rất khẽ.",

        "Miu đứng yên và lắng nghe thật kỹ.",

        "Bống nhẹ nhàng gọi về phía âm thanh để xem ai đang cần giúp đỡ.",

        "Hai người bạn nhìn thấy một chú chim non nhỏ đang ở gần một chiếc tổ.",

        "Chú chim non có vẻ lo lắng vì không thể tìm thấy mẹ.",

        "Miu nhẹ nhàng an ủi chú chim và nói rằng mọi chuyện rồi sẽ ổn.",

        "Bống nhìn lên những cành cây xung quanh để tìm dấu hiệu của chim mẹ.",

        "Sau một lúc tìm kiếm, Bống phát hiện một con đường dẫn đến một cái cây lớn.",

        "Miu và Bống cùng đưa chú chim non đến nơi an toàn.",

        "Từ trên cao, một tiếng chim quen thuộc vang lên.",

        "Chú chim non vui mừng khi nhìn thấy mẹ của mình.",

        "Miu và Bống mỉm cười vì đã giúp được một người bạn nhỏ.",

        "Hai người bạn cùng trở về nhà và hiểu rằng một việc tốt dù nhỏ cũng có thể làm một ngày trở nên thật đẹp.",
    ]


# ============================================================
# TEXT WRAP
# ============================================================

def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""

    for word in words:
        test = word if not current else current + " " + word

        box = draw.textbbox((0, 0), test, font=font)
        width = box[2] - box[0]

        if width <= max_width:
            current = test
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

        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)

        draw.line(
            (0, y, WIDTH, y),
            fill=(r, g, b)
        )


def draw_cloud(draw, x, y, scale=1.0):
    color = (250, 253, 255)

    parts = [
        (-80, 15, 55),
        (0, -15, 75),
        (80, 15, 55),
    ]

    for dx, dy, radius in parts:
        cx = int(x + dx * scale)
        cy = int(y + dy * scale)
        r = int(radius * scale)

        draw.ellipse(
            (cx-r, cy-r, cx+r, cy+r),
            fill=color
        )


def draw_tree(draw, x, y, scale=1.0):
    trunk_w = int(60 * scale)
    trunk_h = int(270 * scale)

    draw.rounded_rectangle(
        (
            x - trunk_w // 2,
            y,
            x + trunk_w // 2,
            y + trunk_h
        ),
        radius=int(18 * scale),
        fill=(110, 75, 48)
    )

    leaves = [
        (-90, -30, 100),
        (0, -90, 125),
        (95, -20, 95),
        (20, 20, 105),
    ]

    for dx, dy, radius in leaves:
        cx = int(x + dx * scale)
        cy = int(y + dy * scale)
        r = int(radius * scale)

        draw.ellipse(
            (cx-r, cy-r, cx+r, cy+r),
            fill=(84, 154, 91)
        )


def draw_bird(draw, x, y, scale=1.0):
    body = (221, 170, 86)
    wing = (194, 139, 65)
    eye = (40, 35, 30)
    beak = (230, 165, 58)

    rx = int(48 * scale)
    ry = int(35 * scale)

    draw.ellipse(
        (x-rx, y-ry, x+rx, y+ry),
        fill=body
    )

    draw.ellipse(
        (
            x-int(5*scale),
            y-int(10*scale),
            x+int(45*scale),
            y+int(25*scale)
        ),
        fill=wing
    )

    eye_r = max(2, int(6 * scale))

    draw.ellipse(
        (
            x+int(18*scale)-eye_r,
            y-int(15*scale)-eye_r,
            x+int(18*scale)+eye_r,
            y-int(15*scale)+eye_r
        ),
        fill=eye
    )

    draw.polygon(
        [
            (x+int(47*scale), y),
            (x+int(75*scale), y+int(9*scale)),
            (x+int(47*scale), y+int(18*scale))
        ],
        fill=beak
    )


# ============================================================
# MIU
# ============================================================

def draw_miu(draw, cx, cy, scale=1.0, emotion="happy"):
    orange = (239, 119, 47)
    orange_light = (255, 145, 60)
    white = (255, 250, 242)
    dark = (55, 38, 32)

    scarf = (151, 205, 230)
    scarf_dot = (248, 252, 255)

    # shadow
    draw.ellipse(
        (
            cx-int(170*scale),
            cy+int(260*scale),
            cx+int(170*scale),
            cy+int(320*scale)
        ),
        fill=(50, 60, 50)
    )

    # tail
    tx = cx + int(150 * scale)
    ty = cy + int(145 * scale)

    draw.ellipse(
        (
            tx-int(120*scale),
            ty-int(80*scale),
            tx+int(100*scale),
            ty+int(100*scale)
        ),
        fill=orange_light
    )

    draw.ellipse(
        (
            tx+int(35*scale),
            ty-int(30*scale),
            tx+int(105*scale),
            ty+int(85*scale)
        ),
        fill=white
    )

    # body
    draw.ellipse(
        (
            cx-int(150*scale),
            cy-int(30*scale),
            cx+int(150*scale),
            cy+int(290*scale)
        ),
        fill=orange
    )

    # belly
    draw.ellipse(
        (
            cx-int(92*scale),
            cy+int(70*scale),
            cx+int(92*scale),
            cy+int(255*scale)
        ),
        fill=white
    )

    # ears
    left_ear = [
        (cx-int(115*scale), cy-int(80*scale)),
        (cx-int(150*scale), cy-int(260*scale)),
        (cx-int(35*scale), cy-int(165*scale))
    ]

    right_ear = [
        (cx+int(35*scale), cy-int(165*scale)),
        (cx+int(150*scale), cy-int(260*scale)),
        (cx+int(115*scale), cy-int(80*scale))
    ]

    draw.polygon(left_ear, fill=orange)
    draw.polygon(right_ear, fill=orange)

    draw.polygon(
        [
            (cx-int(105*scale), cy-int(125*scale)),
            (cx-int(130*scale), cy-int(225*scale)),
            (cx-int(55*scale), cy-int(165*scale))
        ],
        fill=white
    )

    draw.polygon(
        [
            (cx+int(55*scale), cy-int(165*scale)),
            (cx+int(130*scale), cy-int(225*scale)),
            (cx+int(105*scale), cy-int(125*scale))
        ],
        fill=white
    )

    # head
    draw.ellipse(
        (
            cx-int(160*scale),
            cy-int(175*scale),
            cx+int(160*scale),
            cy+int(120*scale)
        ),
        fill=orange_light
    )

    # cheek stripes
    draw.rounded_rectangle(
        (
            cx-int(118*scale),
            cy+int(10*scale),
            cx-int(72*scale),
            cy+int(24*scale)
        ),
        radius=max(2, int(7*scale)),
        fill=white
    )

    draw.rounded_rectangle(
        (
            cx+int(72*scale),
            cy+int(10*scale),
            cx+int(118*scale),
            cy+int(24*scale)
        ),
        radius=max(2, int(7*scale)),
        fill=white
    )

    # eyes
    eye_y = cy - int(60 * scale)

    for ex in (
        cx-int(62*scale),
        cx+int(62*scale)
    ):
        r = int(39 * scale)

        draw.ellipse(
            (ex-r, eye_y-r, ex+r, eye_y+r),
            fill=(255, 255, 255)
        )

        r2 = int(22 * scale)

        draw.ellipse(
            (ex-r2, eye_y-r2, ex+r2, eye_y+r2),
            fill=dark
        )

        draw.ellipse(
            (
                ex-int(8*scale),
                eye_y-int(12*scale),
                ex+int(4*scale),
                eye_y
            ),
            fill=(255, 255, 255)
        )

    # nose
    draw.ellipse(
        (
            cx-int(28*scale),
            cy,
            cx+int(28*scale),
            cy+int(38*scale)
        ),
        fill=(90, 58, 48)
    )

    # mouth
    if emotion == "sad":
        start = 200
        end = 340
    else:
        start = 20
        end = 160

    draw.arc(
        (
            cx-int(35*scale),
            cy+int(15*scale),
            cx+int(35*scale),
            cy+int(75*scale)
        ),
        start,
        end,
        fill=dark,
        width=max(2, int(5*scale))
    )

    # scarf
    scarf_box = (
        cx-int(125*scale),
        cy+int(100*scale),
        cx+int(125*scale),
        cy+int(155*scale)
    )

    draw.rounded_rectangle(
        scarf_box,
        radius=int(25*scale),
        fill=scarf
    )

    # scarf dots
    for dx in (-75, -25, 25, 75):
        r = max(2, int(6*scale))
        x = cx + int(dx*scale)
        y = cy + int(120*scale)

        draw.ellipse(
            (x-r, y-r, x+r, y+r),
            fill=scarf_dot
        )


# ============================================================
# BỐNG
# ============================================================

def draw_bong(draw, cx, cy, scale=1.0):
    cream = (247, 244, 226)
    white = (255, 250, 237)
    pink = (241, 177, 188)
    yellow = (239, 218, 132)
    dark = (62, 54, 48)

    # shadow
    draw.ellipse(
        (
            cx-int(160*scale),
            cy+int(265*scale),
            cx+int(160*scale),
            cy+int(320*scale)
        ),
        fill=(50, 60, 50)
    )

    # body
    draw.ellipse(
        (
            cx-int(145*scale),
            cy,
            cx+int(145*scale),
            cy+int(290*scale)
        ),
        fill=cream
    )

    # overall
    draw.rounded_rectangle(
        (
            cx-int(115*scale),
            cy+int(100*scale),
            cx+int(115*scale),
            cy+int(300*scale)
        ),
        radius=int(40*scale),
        fill=yellow
    )

    # ears
    draw.rounded_rectangle(
        (
            cx-int(135*scale),
            cy-int(270*scale),
            cx-int(35*scale),
            cy-int(35*scale)
        ),
        radius=int(45*scale),
        fill=white
    )

    draw.rounded_rectangle(
        (
            cx+int(35*scale),
            cy-int(280*scale),
            cx+int(135*scale),
            cy-int(30*scale)
        ),
        radius=int(45*scale),
        fill=white
    )

    # inner ears
    draw.rounded_rectangle(
        (
            cx-int(112*scale),
            cy-int(245*scale),
            cx-int(58*scale),
            cy-int(60*scale)
        ),
        radius=int(27*scale),
        fill=pink
    )

    draw.rounded_rectangle(
        (
            cx+int(58*scale),
            cy-int(255*scale),
            cx+int(112*scale),
            cy-int(60*scale)
        ),
        radius=int(27*scale),
        fill=pink
    )

    # head
    draw.ellipse(
        (
            cx-int(160*scale),
            cy-int(180*scale),
            cx+int(160*scale),
            cy+int(115*scale)
        ),
        fill=white
    )

    # eyes
    eye_y = cy - int(62 * scale)

    for ex in (
        cx-int(62*scale),
        cx+int(62*scale)
    ):
        r = int(37*scale)

        draw.ellipse(
            (ex-r, eye_y-r, ex+r, eye_y+r),
            fill=(255, 255, 255)
        )

        r2 = int(20*scale)

        draw.ellipse(
            (ex-r2, eye_y-r2, ex+r2, eye_y+r2),
            fill=dark
        )

        draw.ellipse(
            (
                ex-int(7*scale),
                eye_y-int(11*scale),
                ex+int(3*scale),
                eye_y
            ),
            fill=(255, 255, 255)
        )

    # nose
    draw.ellipse(
        (
            cx-int(18*scale),
            cy,
            cx+int(18*scale),
            cy+int(25*scale)
        ),
        fill=pink
    )

    # mouth
    draw.arc(
        (
            cx-int(35*scale),
            cy+int(12*scale),
            cx+int(35*scale),
            cy+int(62*scale)
        ),
        20,
        160,
        fill=dark,
        width=max(2, int(5*scale))
    )

    # flower behind left ear
    fx = cx-int(135*scale)
    fy = cy-int(175*scale)

    for angle in range(0, 360, 72):
        rad = math.radians(angle)

        px = fx + int(math.cos(rad) * 22 * scale)
        py = fy + int(math.sin(rad) * 22 * scale)

        r = int(15*scale)

        draw.ellipse(
            (px-r, py-r, px+r, py+r),
            fill=pink
        )

    r = int(10*scale)

    draw.ellipse(
        (fx-r, fy-r, fx+r, fy+r),
        fill=(244, 196, 77)
    )


# ============================================================
# SCENE
# ============================================================

def draw_scene(index, text):
    random.seed(1000 + index)

    image = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        (220, 240, 220)
    )

    draw = ImageDraw.Draw(image)

    palettes = [
        ((170, 220, 247), (238, 250, 222)),
        ((190, 225, 250), (239, 247, 219)),
        ((155, 205, 240), (230, 244, 210)),
        ((205, 230, 247), (246, 238, 205)),
    ]

    top, bottom = palettes[index % len(palettes)]

    gradient_background(draw, top, bottom)

    # sun
    draw.ellipse(
        (760, 120, 960, 320),
        fill=(255, 232, 139)
    )

    # clouds
    draw_cloud(draw, 210, 280, 0.9)
    draw_cloud(draw, 820, 430, 0.65)

    # distant hills
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
        fill=(126, 181, 122)
    )

    # ground
    draw.rectangle(
        (0, 1200, WIDTH, HEIGHT),
        fill=(133, 184, 104)
    )

    # path
    draw.polygon(
        [
            (420, HEIGHT),
            (660, HEIGHT),
            (585, 1190),
            (495, 1190),
        ],
        fill=(218, 190, 142)
    )

    # trees
    draw_tree(draw, 130, 820, 0.95)
    draw_tree(draw, 930, 850, 0.85)

    if index % 3 == 0:
        draw_tree(draw, 530, 900, 0.65)

    # flowers
    for _ in range(25):
        x = random.randint(20, WIDTH - 20)
        y = random.randint(1260, HEIGHT - 80)
        r = random.randint(3, 7)

        draw.ellipse(
            (x-r, y-r, x+r, y+r),
            fill=(255, 245, 210)
        )

    # character positions
    positions = [
        (380, 1060, 690, 1080),
        (330, 1050, 720, 1080),
        (420, 1070, 760, 1080),
        (360, 1060, 690, 1090),
    ]

    miu_x, miu_y, bong_x, bong_y = positions[index % 4]

    emotion = "sad" if index in (10, 11, 12, 15) else "happy"

    draw_miu(
        draw,
        miu_x,
        miu_y,
        1.0,
        emotion
    )

    draw_bong(
        draw,
        bong_x,
        bong_y,
        0.92
    )

    # bird
    if index in (0, 1, 2, 3, 4, 5, 6, 12, 13, 14, 15, 16):
        draw_bird(
            draw,
            790,
            970,
            0.75
        )

    # nest
    if index in (14, 15, 16, 17, 18, 19, 20, 21):
        draw.ellipse(
            (770, 990, 980, 1070),
            fill=(125, 86, 50)
        )

        draw.ellipse(
            (800, 1000, 950, 1050),
            fill=(235, 216, 165)
        )

    # scene number
    draw.text(
        (65, 55),
        f"{index + 1:02d}/{SCENE_COUNT:02d}",
        font=FONT_TITLE,
        fill=(255, 255, 255)
    )

    # subtitle card
    card_x1 = 55
    card_y1 = HEIGHT - 355
    card_x2 = WIDTH - 55
    card_y2 = HEIGHT - 55

    draw.rounded_rectangle(
        (
            card_x1,
            card_y1,
            card_x2,
            card_y2
        ),
        radius=35,
        fill=(255, 255, 255)
    )

    lines = wrap_text(
        draw,
        text,
        FONT_SUBTITLE,
        WIDTH - 150
    )

    lines = lines[:4]

    line_height = 48

    total_height = len(lines) * line_height

    start_y = card_y1 + (
        (card_y2 - card_y1 - total_height) // 2
    )

    for line in lines:
        box = draw.textbbox(
            (0, 0),
            line,
            font=FONT_SUBTITLE
        )

        text_width = box[2] - box[0]

        x = (WIDTH - text_width) // 2

        draw.text(
            (x, start_y),
            line,
            font=FONT_SUBTITLE,
            fill=(45, 45, 45)
        )

        start_y += line_height

    return image


# ============================================================
# MAKE FRAMES
# ============================================================

def make_frames(story):
    for old in FRAMES.glob("frame*.png"):
        try:
            old.unlink()
        except Exception:
            pass

    for index, text in enumerate(story):
        print(
            f"[{index + 1}/{len(story)}] Đang tạo cảnh..."
        )

        image = draw_scene(
            index,
            text
        )

        filename = FRAMES / f"frame{index + 1:02d}.png"

        image.save(
            filename,
            "PNG",
            optimize=True
        )

        print(
            f"[{index + 1}/{len(story)}] Đã tạo {filename.name}"
        )


# ============================================================
# TTS
# ============================================================

def make_narration(story):
    """
    Tạo lời đọc tiếng Việt bằng edge-tts.
    Không dùng API key.
    Không có nhạc nền.
    """

    text = " ".join(story)

    text_file = OUT / "narration.txt"
    audio_file = OUT / "narration.mp3"

    text_file.write_text(
        text,
        encoding="utf-8"
    )

    try:
        import edge_tts
        import asyncio
    except ImportError:
        raise RuntimeError(
            "Thiếu edge-tts. "
            "Hãy thêm edge-tts vào requirements.txt."
        )

    voice = os.environ.get(
        "TTS_VOICE",
        "vi-VN-HoaiMyNeural"
    )

    rate = os.environ.get(
        "TTS_RATE",
        "-5%"
    )

    async def generate():
        communicate = edge_tts.Communicate(
            text,
            voice=voice,
            rate=rate,
            volume="+0%"
        )

        await communicate.save(
            str(audio_file)
        )

    asyncio.run(generate())

    print(
        "Đã tạo giọng đọc:",
        audio_file
    )

    return audio_file


# ============================================================
# FFMPEG
# ============================================================

def command_exists(command):
    return shutil.which(command) is not None


def run_command(command):
    print(
        "$",
        " ".join(str(x) for x in command)
    )

    process = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    print(process.stdout)

    if process.returncode != 0:
        raise RuntimeError(
            "FFmpeg thất bại."
        )


# ============================================================
# MAKE VIDEO
# ============================================================

def make_video(audio_file):
    if not command_exists("ffmpeg"):
        raise RuntimeError(
            "Không tìm thấy ffmpeg."
        )

    silent_video = OUT / "silent.mp4"
    final_video = OUT / "video.mp4"

    frame_pattern = str(
        FRAMES / "frame%02d.png"
    )

    # --------------------------------------------------------
    # STEP 1 - IMAGE VIDEO
    # --------------------------------------------------------

    run_command(
        [
            "ffmpeg",
            "-y",

            "-framerate",
            f"1/{SCENE_SECONDS}",

            "-i",
            frame_pattern,

            "-vf",
            (
                f"scale={WIDTH}:{HEIGHT}:"
                "force_original_aspect_ratio=decrease,"
                f"pad={WIDTH}:{HEIGHT}:"
                "(ow-iw)/2:(oh-ih)/2,"
                "format=yuv420p"
            ),

            "-t",
            str(TOTAL_SECONDS),

            "-r",
            str(FPS),

            "-an",

            "-c:v",
            "libx264",

            "-preset",
            "veryfast",

            "-crf",
            "27",

            str(silent_video),
        ]
    )

    # --------------------------------------------------------
    # STEP 2 - ADD VOICE
    # --------------------------------------------------------

    run_command(
        [
            "ffmpeg",
            "-y",

            "-i",
            str(silent_video),

            "-i",
            str(audio_file),

            "-map",
            "0:v:0",

            "-map",
            "1:a:0",

            "-t",
            str(TOTAL_SECONDS),

            "-c:v",
            "copy",

            "-c:a",
            "aac",

            "-b:a",
            "128k",

            "-af",
            "apad",

            "-shortest",

            "-movflags",
            "+faststart",

            str(final_video),
        ]
    )

    return final_video


# ============================================================
# SAVE CHARACTERS.JSON
# ============================================================

def save_characters():
    file = OUT / "characters.json"

    data = {
        "CHAR_01": CHARACTERS["CHAR_01"],
        "CHAR_02": CHARACTERS["CHAR_02"],
    }

    file.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("AI VIDEO MAKER")
    print("FREE RENDER MODE")
    print("=" * 70)

    topic = get_prompt()

    print("Chủ đề:")
    print(topic)

    print()
    print("Thời lượng:", TOTAL_SECONDS, "giây")
    print("Số cảnh:", SCENE_COUNT)
    print("Nhạc nền: TẮT")
    print("FLUX API: TẮT")
    print("Hugging Face Image API: TẮT")
    print("=" * 70)

    # --------------------------------------------------------
    # STORY
    # --------------------------------------------------------

    story = make_story(topic)

    # Save story
    story_file = OUT / "story.json"

    story_file.write_text(
        json.dumps(
            {
                "topic": topic,
                "duration": TOTAL_SECONDS,
                "scene_count": SCENE_COUNT,
                "scenes": story,
            },
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    save_characters()

    # --------------------------------------------------------
    # FRAMES
    # --------------------------------------------------------

    print()
    print("BƯỚC 1/3 - TẠO CẢNH")
    print()

    make_frames(story)

    # --------------------------------------------------------
    # VOICE
    # --------------------------------------------------------

    print()
    print("BƯỚC 2/3 - TẠO GIỌNG VIỆT")
    print()

    audio = make_narration(story)

    # --------------------------------------------------------
    # VIDEO
    # --------------------------------------------------------

    print()
    print("BƯỚC 3/3 - GHÉP VIDEO")
    print()

    video = make_video(audio)

    # --------------------------------------------------------
    # DONE
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("HOÀN TẤT")
    print("=" * 70)
    print("VIDEO:")
    print(video)
    print("=" * 70)


if __name__ == "__main__":
    main()
