from PIL import Image, ImageDraw

prompt = open("prompt.txt","r",encoding="utf-8").read()

img = Image.new("RGB",(720,1280),(135,206,235))
d = ImageDraw.Draw(img)
d.text((40,80),"AI VIDEO MAKER",fill="white")
d.text((40,160),prompt[:120],fill="black")

img.save("frame1.png")
