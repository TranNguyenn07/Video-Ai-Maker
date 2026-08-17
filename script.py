
import os

topic = os.environ["PROMPT"]

scenes = []

for i in range(24):
    if i == 0:
        text = f"Miu và Bống bắt đầu cuộc phiêu lưu: {topic}."
    elif i == 23:
        text = "Miu và Bống chào tạm biệt các bạn nhỏ."
    else:
        text = f"Cảnh {i+1}: {topic}, hai bạn cùng nhau vượt qua thử thách."

    scenes.append(text)

open("story.txt","w",encoding="utf-8").write("\n".join(scenes))
