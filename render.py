import requests, os

PROMPT = open("prompt.txt","r",encoding="utf-8").read()
API = os.environ["HF_TOKEN"]

r = requests.post(
    "https://router.huggingface.co/fal-ai/fal-ai/flux/schnell",
    headers={"Authorization": f"Bearer {API}"},
    json={"prompt": PROMPT}
)

print(r.json())
