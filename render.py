import os, json, asyncio, requests, edge_tts

# Đọc prompt
story = open("prompt.txt","r",encoding="utf-8").read()

# Đọc nhân vật
cfg = json.load(open("characters.json",encoding="utf-8"))
miu = cfg["characters"]["miu"]
bong = cfg["characters"]["bong"]

TOKEN = os.environ["HF_TOKEN"]
API = "https://router.huggingface.co/fal-ai/fal-ai/flux/schnell"

# Khóa thiết kế nhân vật
LOCK = f"""
3D animated movie, Pixar quality, vertical 9:16.

CHAR_01:
{miu["lock"]}

CHAR_02:
{bong["lock"]}

Never redesign the characters.
"""

# Tạo 24 ảnh
for i in range(1,25):
    prompt = f"{LOCK}\nStory:{story}\nScene {i}/24"
    r = requests.post(
        API,
        headers={"Authorization":f"Bearer {TOKEN}"},
        json={"prompt":prompt}
    )
    open(f"frame{i}.png","wb").write(r.content)

# Lời thoại tiếng Việt
voice_text = f"""
Ngày xửa ngày xưa, {story}
Miu và Bống luôn giúp đỡ mọi người.
Nhờ lòng tốt, mọi khó khăn đều được vượt qua.
Hẹn gặp lại các bạn ở tập tiếp theo.
"""

async def make_voice():
    tts = edge_tts.Communicate(
        voice_text,
        "vi-VN-HoaiMyNeural"
    )
    await tts.save("voice.mp3")

asyncio.run(make_voice())
