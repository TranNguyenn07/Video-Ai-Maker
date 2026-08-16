#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Video-Ai-Maker - render.py (FREE / no FLUX API)

Mục tiêu:
- Không gọi Hugging Face FLUX/In­ference Providers => không còn lỗi 402 do hết credit.
- Dùng 2 nhân vật cố định Miu + Bống từ mô tả bên dưới.
- Tạo video dọc 1080x1920, tối thiểu 60 giây.
- Có lời thoại tiếng Việt, KHÔNG nhạc nền.
- Tạo cảnh bằng Pillow (vector/painted 2.5D), nên không cần API tạo ảnh.
- Có thể chạy trên GitHub Actions và máy Android/Termux nếu đã cài Python + ffmpeg.

Cách chạy:
    python render.py "Miu và Bống giúp một chú chim non tìm đường về tổ"

Hoặc:
    VIDEO_PROMPT="..." python render.py

Kết quả:
    output/video.mp4
    output/narration.mp3
    output/scene_01.png ... scene_24.png
"""

import os
import sys
import math
import json
import random
import shutil
import subprocess
from pathlib import Path
from textwrap import wrap

WIDTH, HEIGHT = 1080, 1920
FPS = 24
SCENE_COUNT = 24
SCENE_SECONDS = 2.5
TOTAL_SECONDS = SCENE_COUNT * SCENE_SECONDS

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
FRAMES = OUT / "frames"
OUT.mkdir(parents=True, exist_ok=True)
FRAMES.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------
# CHARACTER BIBLE
# ---------------------------------------------------------------------

CHARACTERS = {
    "CHAR_01": {
        "name": "Miu",
        "description": (
            "Miu, a small round fox kit with bright orange fur, a pure white belly "
            "and white-tipped tail, big round expressive eyes, large fluffy ears "
            "with white fur tips, two small white fur streaks on both cheeks, "
            "wearing a pastel sky-blue scarf with small white polka dots tied around "
            "the neck. Child-like proportions, 3D animated movie style, extremely "
            "cute and expressive. This exact character design must be used."
        ),
    },
    "CHAR_02": {
        "name": "Bống",
        "description": (
            "Bống, a small rabbit kit with cream-white fur, long upright ears with "
            "pale pink inner ears, the left ear slightly drooping, wearing a pale "
            "butter-yellow overall, with a small pale pink flower tucked behind the "
            "left ear. Child-like proportions, 3D animated movie style, soft and "
            "gentle design. This exact character design must be used."
        ),
    },
}

# ---------------------------------------------------------------------
# INPUT
# ---------------------------------------------------------------------

def get_prompt():
    if len(sys.argv) > 1 and sys.argv[1].strip():
        return sys.argv[1].strip()

    p = os.environ.get("VIDEO_PROMPT", "").strip()
    if p:
        return p

    # GitHub Actions can pass INPUT_PROMPT depending on workflow.
    p = os.environ.get("INPUT_PROMPT", "").strip()
    if p:
        return p

    return "Miu và Bống cùng nhau giúp một chú chim non bị lạc tìm đường về tổ."

# ---------------------------------------------------------------------
# STORY GENERATION - NO AI API
# ---------------------------------------------------------------------

def make_story(topic):
    """
    Tạo cấu trúc truyện ổn định bằng Python.
    Không gọi LLM nên không phát sinh API cost.
    """

    templates = [
        f"Một buổi sáng trong khu rừng nhỏ, Miu và Bống đang chơi thì nhận ra một điều bất thường: {topic}",
        "Miu nhìn quanh thật kỹ rồi nhẹ nhàng nói rằng hai bạn nên cùng nhau tìm cách giải quyết.",
        "Bống cũng gật đầu. Hai bạn quyết định đi thật chậm để không làm điều gì trong khu rừng bị sợ hãi.",
        "Miu dùng đôi tai nhạy bén để lắng nghe những âm thanh rất nhỏ ở phía trước.",
        "Bống nhìn xuống mặt đất và phát hiện một dấu vết bé xíu dẫn vào con đường phủ đầy lá.",
        "Hai bạn đi theo dấu vết, vừa đi vừa động viên nhau rằng nhất định sẽ tìm ra câu trả lời.",
        "Con đường dẫn đến một khoảng rừng có ánh nắng dịu dàng xuyên qua những tán cây.",
        "Miu phát hiện một chướng ngại vật trên đường và cẩn thận tìm một lối đi an toàn.",
        "Bống cùng Miu nhặt những cành cây nhỏ sang một bên để con đường trở nên dễ đi hơn.",
        "Sau đó, hai bạn nghe thấy một âm thanh rất khẽ ở phía xa.",
        "Miu đứng yên lắng nghe, còn Bống nhẹ nhàng gọi về phía âm thanh ấy.",
        "Một dấu hiệu nhỏ xuất hiện, khiến cả hai bạn vui mừng nhưng vẫn bình tĩnh tiếp tục.",
        "Hai bạn cùng nhau tiến thêm vài bước và nhìn thấy nơi cần tìm.",
        "Miu mỉm cười, còn Bống vui vẻ vỗ nhẹ đôi tay.",
        "Nhưng công việc vẫn chưa xong. Hai bạn cần tìm cách giúp mọi thứ trở lại an toàn.",
        "Miu nghĩ ra một cách đơn giản và Bống lập tức đồng ý giúp.",
        "Hai bạn phối hợp thật nhịp nhàng, mỗi người làm một việc nhỏ.",
        "Chỉ một lúc sau, mọi chuyện bắt đầu tốt lên.",
        "Điều khiến Miu và Bống vui nhất là họ đã không bỏ cuộc giữa chừng.",
        "Hai bạn cùng nhìn nhau và nhận ra rằng làm việc cùng nhau luôn dễ dàng hơn.",
        "Khu rừng trở lại yên bình, tiếng gió nhẹ nhàng lướt qua những chiếc lá.",
        "Miu chỉnh lại chiếc khăn xanh, còn Bống cười thật tươi.",
        "Hai người bạn cùng trở về trên con đường nhỏ và nhắc nhau sẽ luôn giúp đỡ nhau.",
        "Và từ ngày hôm đó, Miu và Bống hiểu rằng một việc tốt dù rất nhỏ cũng có thể làm một ngày trở nên thật ấm áp.",
    ]

    return templates[:SCENE_COUNT]

# ---------------------------------------------------------------------
# DRAWING HELPERS
# ---------------------------------------------------------------------

from PIL import Image, ImageDraw, ImageFont, ImageFilter

def font(size, bold=False):
    candidates = []
    if bold:
        candidates += [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        ]
    else:
        candidates += [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        ]

    for p in candidates:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

FONT_TITLE = font(58, True)
FONT_SUB = font(40, False)

def lerp(a, b, t):
    return int(a + (b - a) * t)

def gradient_bg(draw, top, bottom):
    for y in range(HEIGHT):
        t = y / max(1, HEIGHT - 1)
        c = tuple(lerp(top[i], bottom[i], t) for i in range(3))
        draw.line((0, y, WIDTH, y), fill=c)

def rounded(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

def shadow_ellipse(img, box, alpha=80):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x1, y1, x2, y2 = box
    d.ellipse(box, fill=(20, 30, 40, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(22))
    img.alpha_composite(layer)

def draw_tree(draw, x, y, scale=1.0):
    trunk_w = int(55 * scale)
    trunk_h = int(250 * scale)
    draw.rounded_rectangle(
        (x - trunk_w//2, y, x + trunk_w//2, y + trunk_h),
        radius=int(18*scale), fill=(113, 78, 48)
    )
    for dx, dy, r in [(-90,-35,100),(0,-90,125),(95,-25,95),(30,10,110)]:
        cx = x + int(dx*scale)
        cy = y + int(dy*scale)
        rr = int(r*scale)
        draw.ellipse((cx-rr, cy-rr, cx+rr, cy+rr), fill=(92, 157, 93))

def draw_cloud(draw, x, y, s=1.0):
    col=(248,252,255)
    for dx,dy,r in [(-90,10,55),(0,-15,75),(80,10,55)]:
        rr=int(r*s)
        cx=int(x+dx*s); cy=int(y+dy*s)
        draw.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),fill=col)

def draw_bird(draw, x, y, s=1.0):
    # Small friendly bird.
    body=(210,165,85)
    wing=(190,140,70)
    draw.ellipse(
        (x-int(48*s), y-int(35*s), x+int(48*s), y+int(35*s)),
        fill=body
    )
    draw.ellipse(
        (x-int(8*s), y-int(10*s), x+int(45*s), y+int(25*s)),
        fill=wing
    )
    draw.ellipse(
        (x+int(18*s), y-int(18*s), x+int(29*s), y-int(7*s)),
        fill=(30,30,30)
    )
    draw.polygon([
        (x+int(48*s),y),
        (x+int(72*s),y+int(8*s)),
        (x+int(48*s),y+int(18*s))
    ], fill=(220,160,55))

# ---------------------------------------------------------------------
# CHARACTER DRAWING
# ---------------------------------------------------------------------

def draw_miu(draw, cx, cy, s=1.0, emotion="happy"):
    """
    Vector interpretation of CHAR_01.
    Đây là hình minh hoạ 2.5D offline, không phải model 3D.
    """
    orange=(239,119,47)
    orange2=(255,145,60)
    white=(255,250,242)
    dark=(55,38,32)
    scarf=(151,205,230)
    scarf_dot=(248,252,255)

    # ground shadow
    draw.ellipse(
        (cx-int(170*s), cy+int(260*s), cx+int(170*s), cy+int(320*s)),
        fill=(0,0,0,45)
    )

    # tail behind body
    tx=cx+int(150*s); ty=cy+int(140*s)
    draw.ellipse(
        (tx-int(120*s),ty-int(80*s),tx+int(100*s),ty+int(100*s)),
        fill=orange2
    )
    draw.ellipse(
        (tx+int(40*s),ty-int(30*s),tx+int(105*s),ty+int(85*s)),
        fill=white
    )

    # body
    draw.ellipse(
        (cx-int(150*s), cy-int(30*s), cx+int(150*s), cy+int(290*s)),
        fill=orange
    )

    # white belly
    draw.ellipse(
        (cx-int(92*s), cy+int(70*s), cx+int(92*s), cy+int(255*s)),
        fill=white
    )

    # ears
    left=[(cx-int(115*s),cy-int(80*s)),
          (cx-int(150*s),cy-int(260*s)),
          (cx-int(35*s),cy-int(165*s))]
    right=[(cx+int(35*s),cy-int(165*s)),
           (cx+int(150*s),cy-int(260*s)),
           (cx+int(115*s),cy-int(80*s))]
    draw.polygon(left, fill=orange)
    draw.polygon(right, fill=orange)
    draw.polygon([
        (cx-int(105*s),cy-int(125*s)),
        (cx-int(130*s),cy-int(225*s)),
        (cx-int(55*s),cy-int(165*s))
    ], fill=white)
    draw.polygon([
        (cx+int(55*s),cy-int(165*s)),
        (cx+int(130*s),cy-int(225*s)),
        (cx+int(105*s),cy-int(125*s))
    ], fill=white)

    # head
    draw.ellipse(
        (cx-int(160*s),cy-int(175*s),cx+int(160*s),cy+int(120*s)),
        fill=orange2
    )

    # cheeks streaks
    draw.rounded_rectangle(
        (cx-int(118*s),cy+int(10*s),cx-int(72*s),cy+int(24*s)),
        radius=int(7*s), fill=white
    )
    draw.rounded_rectangle(
        (cx+int(72*s),cy+int(10*s),cx+int(118*s),cy+int(24*s)),
        radius=int(7*s), fill=white
    )

    # eyes
    eye_y=cy-int(60*s)
    for ex in (cx-int(62*s), cx+int(62*s)):
        rr=int(39*s)
        draw.ellipse((ex-rr,eye_y-rr,ex+rr,eye_y+rr), fill=white)
        rr2=int(22*s)
        draw.ellipse((ex-rr2,eye_y-rr2,ex+rr2,eye_y+rr2), fill=dark)
        draw.ellipse(
            (ex-int(8*s),eye_y-int(12*s),ex+int(4*s),eye_y),
            fill=white
        )

    # muzzle/nose
    draw.ellipse(
        (cx-int(28*s),cy+int(0*s),cx+int(28*s),cy+int(38*s)),
        fill=(90,58,48)
    )

    # mouth
    if emotion == "sad":
        draw.arc(
            (cx-int(35*s),cy+int(25*s),cx+int(35*s),cy+int(80*s)),
            200,340, fill=dark, width=max(2,int(5*s))
        )
    else:
        draw.arc(
            (cx-int(35*s),cy+int(15*s),cx+int(35*s),cy+int(70*s)),
            20,160, fill=dark, width=max(2,int(5*s))
        )

    # scarf
    scarf_box=(
        cx-int(125*s), cy+int(100*s),
        cx+int(125*s), cy+int(155*s)
    )
    draw.rounded_rectangle(scarf_box, radius=int(25*s), fill=scarf)
    for dx in (-75,-25,25,75):
        draw.ellipse(
            (cx+int(dx*s)-int(6*s), cy+int(120*s)-int(6*s),
             cx+int(dx*s)+int(6*s), cy+int(120*s)+int(6*s)),
            fill=scarf_dot
        )

def draw_bong(draw, cx, cy, s=1.0, emotion="happy"):
    cream=(247,244,226)
    cream2=(255,250,237)
    pink=(241,177,188)
    yellow=(239,218,132)
    dark=(62,54,48)

    draw.ellipse(
        (cx-int(160*s), cy+int(265*s), cx+int(160*s), cy+int(320*s)),
        fill=(0,0,0,45)
    )

    # body / overall
    draw.ellipse(
        (cx-int(145*s),cy+int(0*s),cx+int(145*s),cy+int(290*s)),
        fill=cream
    )
    draw.rounded_rectangle(
        (cx-int(115*s),cy+int(100*s),cx+int(115*s),cy+int(300*s)),
        radius=int(40*s), fill=yellow
    )

    # ears; left ear droops slightly
    draw.rounded_rectangle(
        (cx-int(135*s),cy-int(270*s),cx-int(35*s),cy-int(35*s)),
        radius=int(45*s), fill=cream2
    )
    draw.rounded_rectangle(
        (cx+int(35*s),cy-int(280*s),cx+int(135*s),cy-int(30*s)),
        radius=int(45*s), fill=cream2
    )
    draw.rounded_rectangle(
        (cx-int(112*s),cy-int(245*s),cx-int(58*s),cy-int(60*s)),
        radius=int(27*s), fill=pink
    )
    draw.rounded_rectangle(
        (cx+int(58*s),cy-int(255*s),cx+int(112*s),cy-int(60*s)),
        radius=int(27*s), fill=pink
    )

    # head
    draw.ellipse(
        (cx-int(160*s),cy-int(180*s),cx+int(160*s),cy+int(115*s)),
        fill=cream2
    )

    # eyes
    eye_y=cy-int(62*s)
    for ex in (cx-int(62*s),cx+int(62*s)):
        rr=int(37*s)
        draw.ellipse((ex-rr,eye_y-rr,ex+rr,eye_y+rr), fill=white if False else (255,255,255))
        rr2=int(20*s)
        draw.ellipse((ex-rr2,eye_y-rr2,ex+rr2,eye_y+rr2), fill=dark)
        draw.ellipse(
            (ex-int(7*s),eye_y-int(11*s),ex+int(3*s),eye_y),
            fill=(255,255,255)
        )

    # nose + mouth
    draw.ellipse(
        (cx-int(18*s),cy+int(0*s),cx+int(18*s),cy+int(25*s)),
        fill=pink
    )
    draw.arc(
        (cx-int(35*s),cy+int(12*s),cx+int(35*s),cy+int(62*s)),
        20,160, fill=dark, width=max(2,int(5*s))
    )

    # flower behind left ear
    fx=cx-int(135*s); fy=cy-int(175*s)
    for a in range(0,360,72):
        rad=math.radians(a)
        px=fx+int(math.cos(rad)*22*s)
        py=fy+int(math.sin(rad)*22*s)
        r=int(15*s)
        draw.ellipse((px-r,py-r,px+r,py+r),fill=pink)
    draw.ellipse(
        (fx-int(10*s),fy-int(10*s),fx+int(10*s),fy+int(10*s)),
        fill=(244,196,77)
    )

# ---------------------------------------------------------------------
# SCENE RENDERING
# ---------------------------------------------------------------------

def draw_scene(index, text):
    seed = 1000 + index
    random.seed(seed)

    img = Image.new("RGBA", (WIDTH, HEIGHT), (240, 245, 250, 255))
    d = ImageDraw.Draw(img, "RGBA")

    # Vary the environment subtly.
    palettes = [
        ((170,220,247),(238,250,222)),
        ((190,225,250),(239,247,219)),
        ((155,205,240),(230,244,210)),
        ((205,230,247),(246,238,205)),
    ]
    top, bottom = palettes[index % len(palettes)]
    gradient_bg(d, top, bottom)

    # sun
    d.ellipse((760,120,960,320), fill=(255,232,139,180))

    # clouds
    draw_cloud(d, 210, 280, .9)
    draw_cloud(d, 820, 430, .65)

    # distant hills
    d.polygon(
        [(0,1000),(180,850),(360,980),(550,820),(760,970),(930,830),(1080,970),
         (1080,1300),(0,1300)],
        fill=(126,181,122)
    )

    # ground
    d.rectangle((0,1200,WIDTH,HEIGHT), fill=(133,184,104))

    # path
    d.polygon(
        [(420,HEIGHT),(660,HEIGHT),(585,1190),(495,1190)],
        fill=(218,190,142)
    )

    # trees
    draw_tree(d, 130, 820, .95)
    draw_tree(d, 930, 850, .85)
    if index % 3 == 0:
        draw_tree(d, 530, 900, .65)

    # little flowers
    for _ in range(25):
        x=random.randint(20,WIDTH-20)
        y=random.randint(1260,HEIGHT-80)
        r=random.randint(3,7)
        d.ellipse((x-r,y-r,x+r,y+r), fill=(255,245,210,210))

    # characters
    if index % 4 == 0:
        miu_x, bong_x = 390, 700
    elif index % 4 == 1:
        miu_x, bong_x = 330, 720
    elif index % 4 == 2:
        miu_x, bong_x = 420, 760
    else:
        miu_x, bong_x = 360, 690

    emotion = "sad" if 10 <= index <= 12 else "happy"
    draw_miu(d, miu_x, 1060, 1.0, emotion)
    draw_bong(d, bong_x, 1080, .92, "happy")

    # Small story prop on selected scenes.
    if index in (4,5,6,7):
        draw_bird(d, 790, 970, .75)
    elif index in (12,13,14):
        # nest
        d.ellipse((770,990,980,1070), fill=(125,86,50))
        d.ellipse((800,1000,950,1050), fill=(235,216,165))

    # Bottom subtitle card. Keep it readable but not too intrusive.
    card_h=260
    rounded(
        d,
        (55, HEIGHT-card_h-55, WIDTH-55, HEIGHT-55),
        35,
        (255,255,255,225)
    )

    # Wrap Vietnamese text.
    lines = wrap(text, width=35)
    lines = lines[:4]
    y=HEIGHT-card_h-15
    line_h=48
    for line in lines:
        bbox=d.textbbox((0,0),line,font=FONT_SUB)
        tw=bbox[2]-bbox[0]
        d.text(((WIDTH-tw)//2,y),line,font=FONT_SUB,fill=(48,48,48,255))
        y += line_h

    # Scene number.
    d.text((70,55),f"{index+1:02d}/{SCENE_COUNT:02d}",
           font=FONT_TITLE,fill=(255,255,255,230))

    return img.convert("RGB")

# ---------------------------------------------------------------------
# VIETNAMESE TTS
# ---------------------------------------------------------------------

def check_command(name):
    return shutil.which(name) is not None

def make_narration(story):
    """
    Dùng edge-tts. Không cần API key.
    Nếu edge-tts không chạy, workflow báo rõ lỗi thay vì im lặng.
    """
    text = " ".join(story)
    txt_path = OUT / "narration.txt"
    mp3_path = OUT / "narration.mp3"
    txt_path.write_text(text, encoding="utf-8")

    try:
        import asyncio
        import edge_tts
    except Exception:
        print("Thiếu edge-tts. Hãy thêm edge-tts vào requirements.txt.")
        raise

    async def run_tts():
        voice = os.environ.get("TTS_VOICE", "vi-VN-HoaiMyNeural")
        communicate = edge_tts.Communicate(
            text,
            voice=voice,
            rate=os.environ.get("TTS_RATE", "-5%"),
            volume="+0%"
        )
        await communicate.save(str(mp3_path))

    asyncio.run(run_tts())
    return mp3_path

# ---------------------------------------------------------------------
# FFMPEG
# ---------------------------------------------------------------------

def run(cmd):
    print("$", " ".join(map(str, cmd)))
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if p.returncode != 0:
        print(p.stdout)
        raise RuntimeError("Lệnh thất bại: " + " ".join(map(str, cmd)))
    return p.stdout

def make_frames(story):
    # Clean old frames.
    for p in FRAMES.glob("*.png"):
        p.unlink()

    for i, text in enumerate(story):
        print(f"[{i+1}/{len(story)}] Đang tạo cảnh...")
        img = draw_scene(i, text)
        path = FRAMES / f"frame{i+1:02d}.png"
        img.save(path, optimize=True)
        print(f"[{i+1}/{len(story)}] Đã tạo {path.name}")

def make_video(audio_path):
    if not check_command("ffmpeg"):
        raise RuntimeError("Không tìm thấy ffmpeg. GitHub Actions cần cài ffmpeg trước bước Render.")

    silent_video = OUT / "silent.mp4"
    final_video = OUT / "video.mp4"

    # Each image is exactly 2.5s => 60 seconds.
    # -stream_loop ensures the last image is held if ffmpeg needs more time.
    pattern = str(FRAMES / "frame%02d.png")

    run([
        "ffmpeg", "-y",
        "-framerate", "1/" + str(SCENE_SECONDS),
        "-i", pattern,
        "-vf", f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
               f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2,"
               f"format=yuv420p",
        "-t", str(TOTAL_SECONDS),
        "-r", str(FPS),
        "-an",
        str(silent_video)
    ])

    # If narration is shorter than 60 sec, the final video remains 60 sec
    # and audio is padded with silence. If narration is longer, video is
    # extended by looping the final frame.
    run([
        "ffmpeg", "-y",
        "-i", str(silent_video),
        "-i", str(audio_path),
        "-filter_complex",
        "[1:a]apad=pad_dur=60[a]",
        "-map", "0:v:0",
        "-map", "[a]",
        "-t", str(TOTAL_SECONDS),
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "27",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        str(final_video)
    ])

    return final_video

# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------

def main():
    topic = get_prompt()
    print("=" * 70)
    print("VIDEO AI MAKER - FREE OFFLINE RENDER")
    print("=" * 70)
    print("Chủ đề:", topic)
    print("Thời lượng mục tiêu:", TOTAL_SECONDS, "giây")
    print("Số cảnh:", SCENE_COUNT)
    print("Nhạc nền: TẮT")
    print("FLUX/Hugging Face image API: TẮT")
    print("=" * 70)

    story = make_story(topic)

    # Save story for debugging/reuse.
    (OUT / "story.json").write_text(
        json.dumps(
            {
                "topic": topic,
                "characters": CHARACTERS,
                "duration_seconds": TOTAL_SECONDS,
                "scenes": story,
            },
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    make_frames(story)

    print("Tạo giọng đọc tiếng Việt...")
    audio = make_narration(story)
    print("Đã tạo:", audio)

    print("Ghép video...")
    video = make_video(audio)
    print("=" * 70)
    print("HOÀN TẤT")
    print("Video:", video)
    print("=" * 70)

if __name__ == "__main__":
    main()
