import os

prompt = os.environ["PROMPT"]

scenes = []
for i in range(1, 25):
    scenes.append(f"Cảnh {i}: {prompt}")

with open("story.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(scenes))
