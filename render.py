
from PIL import Image, ImageDraw
import requests, urllib.parse, asyncio, edge_tts

# Đọc 24 cảnh
scenes = open("story.txt","r",encoding="utf-8").read().splitlines()

# Nhân vật
miu = Image.open("assets/characters/miu.png").convert("RGBA")
bong = Image.open("assets/characters/bong.png").convert("RGBA")

miu = miu.resize((250,250))
bong = bong.resize((230,230))

voice_text = []

for i, scene in enumerate(scenes,1):

    prompt = urllib.parse.quote(
        f"cute 3D Pixar forest, pastel, children animation, {scene}"
    )

    bg = requests.get(
        "https://image.pollinations.ai/prompt/"+prompt,
        timeout=60
    )

    open("bg.png","wb").write(bg.content)

    img = Image.open("bg.png").convert("RGBA")

    # Vị trí nhân vật
    x1 = 70 + (i%3)*25
    x2 = 390 - (i%2)*20

    img.alpha_composite(miu,(x1,770))
    img.alpha_composite(bong,(x2,790))

    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle(
        (25,40,695,180),
        radius=25,
        fill=(255,255,255,210)
    )

    draw.text((45,60),f"Scene {i}",fill="orange")
    draw.text((45,105),scene,fill="black")

    img.convert("RGB").save(f"frame{i}.png")
    voice_text.append(scene)

async def make_voice():
    tts = edge_tts.Communicate(
        " ".join(voice_text),
        "vi-VN-HoaiMyNeural"
    )
    await tts.save("voice.mp3")

asyncio.run(make_voice())
