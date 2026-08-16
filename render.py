import json
from PIL import Image, ImageDraw

cfg = json.load(open("characters.json", encoding="utf-8"))

MIU = cfg["characters"]["miu"]
BONG = cfg["characters"]["bong"]

SCENES = [
    "Miu gặp Bống trong rừng",
    "Hai bạn phát hiện hạt giống",
    "Cùng trồng cây",
    "Tưới nước và chăm sóc",
    "Cây nở hoa rực rỡ",
    "Kết thúc hạnh phúc"
]

W, H = 720, 1280

for i, scene in enumerate(SCENES, 1):
    img = Image.new("RGB", (W, H), (210, 240, 255))
    d = ImageDraw.Draw(img)

    d.text((30,40), "AI VIDEO MAKER", fill="black")
    d.text((30,110), f"Scene {i}", fill="red")
    d.text((30,180), scene, fill="black")

    d.text((30,320), "CHAR_01", fill=(255,120,0))
    d.text((30,360), MIU["name"], fill=(255,120,0))
    d.text((30,400), MIU["accessory"], fill="black")

    d.text((30,560), "CHAR_02", fill=(255,180,0))
    d.text((30,600), BONG["name"], fill=(255,180,0))
    d.text((30,640), BONG["accessory"], fill="black")

    img.save(f"frame{i}.png")

print("Created 6 frames")
