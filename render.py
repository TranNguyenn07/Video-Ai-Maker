from PIL import Image, ImageDraw
import os

prompt = "Miu và Bống"

for i in range(1,6):
    img = Image.new("RGB",(720,1280),(180,230,255))
    d = ImageDraw.Draw(img)

    d.text((40,60),"AI VIDEO MAKER",fill="black")
    d.text((40,140),prompt,fill="blue")
    d.text((40,220),f"Scene {i}",fill="red")

    img.save(f"frame{i}.png")
