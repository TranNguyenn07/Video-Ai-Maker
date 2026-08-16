from PIL import Image, ImageDraw

for i in range(1,6):
    img=Image.new("RGB",(720,1280),(135,206,235))
    d=ImageDraw.Draw(img)
    d.text((40,80),f"Scene {i}",fill="white")
    img.save(f"frame{i}.png")
