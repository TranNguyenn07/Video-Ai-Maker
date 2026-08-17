
from PIL import Image
import asyncio, edge_tts

miu = Image.open("assets/characters/miu.png").convert("RGBA").resize((240,240))
bong = Image.open("assets/characters/bong.png").convert("RGBA").resize((220,220))

story = open("story.txt",encoding="utf-8").read().splitlines()

voice = []

for i, s in enumerate(story, 1):
    bg = Image.new("RGBA",(720,1280),(210,240,255,255))
    bg.alpha_composite(miu,(60+(i%3)*30,760))
    bg.alpha_composite(bong,(390-(i%2)*25,790))
    bg.convert("RGB").save(f"frame{i}.png")
    voice.append(s)

async def make():
    await edge_tts.Communicate(
        " ".join(voice),
        "vi-VN-HoaiMyNeural"
    ).save("voice.mp3")

asyncio.run(make())
