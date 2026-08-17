from PIL import Image
import requests, urllib.parse, asyncio, edge_tts

scenes=open("story.txt",encoding="utf-8").read().splitlines()

miu=Image.open("assets/characters/miu.png").convert("RGBA").resize((260,260))
bong=Image.open("assets/characters/bong.png").convert("RGBA").resize((220,220))

voice=[]

for i,s in enumerate(scenes,1):
    q=urllib.parse.quote(
      f"cute 2D children storybook forest, pastel, {s}"
    )
    bg=requests.get("https://image.pollinations.ai/prompt/"+q,timeout=60).content
    open("bg.png","wb").write(bg)

    img=Image.open("bg.png").convert("RGBA")
    img.alpha_composite(miu,(60+(i%4)*20,760))
    img.alpha_composite(bong,(400-(i%3)*25,790))
    img.convert("RGB").save(f"frame{i}.png")
    voice.append(s)

async def tts():
    await edge_tts.Communicate(
      " ".join(voice),
      "vi-VN-HoaiMyNeural"
    ).save("voice.mp3")

asyncio.run(tts())
