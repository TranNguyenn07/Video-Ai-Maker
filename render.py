import json, os, requests

cfg = json.load(open("characters.json",encoding="utf-8"))
prompt = open("prompt.txt",encoding="utf-8").read()

TOKEN = os.environ["HF_TOKEN"]
API = "https://router.huggingface.co/fal-ai/fal-ai/flux/schnell"

CHAR = f"""
{cfg["characters"]["miu"]["lock"]}
{cfg["characters"]["bong"]["lock"]}
3D Pixar kids animation, keep same characters.
"""

for i in range(1,7):
    r = requests.post(
        API,
        headers={"Authorization":f"Bearer {TOKEN}"},
        json={"prompt":f"{CHAR}\nScene {i}: {prompt}"}
    )
    open(f"frame{i}.png","wb").write(r.content)
