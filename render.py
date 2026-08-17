from PIL import Image
import asyncio,edge_tts

miu=Image.open("assets/characters/miu.png").convert("RGBA").resize((230,230))
bong=Image.open("assets/characters/bong.png").convert("RGBA").resize((210,210))

story=open("story.txt",encoding="utf-8").read().splitlines()

voice=[]

for i,s in enumerate(story,1):
    bg=Image.new("RGBA",(720,1280),(190,235,255,255))

    x1=40+i*12
    x2=430-i*8

    bg.alpha_composite(miu,(x1,780))
    bg.alpha_composite(bong,(x2,800))

    bg.convert("RGB").save(f"frame{i}.png")
    voice.append(s)

async def tts():
    await edge_tts.Communicate(
        " ".join(voice),
        "vi-VN-HoaiMyNeural"
    ).save("voice.mp3")

asyncio.run(tts())
