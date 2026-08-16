import os
import json
import asyncio
import base64
import requests
import edge_tts
from pathlib import Path


# =========================================================
# 1. ĐỌC DỮ LIỆU
# =========================================================

with open("prompt.txt", "r", encoding="utf-8") as f:
    user_prompt = f.read().strip()

with open("characters.json", "r", encoding="utf-8") as f:
    characters = json.load(f)

HF_TOKEN = os.environ.get("HF_TOKEN")

if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN chưa được thiết lập trong GitHub Secrets.")

if not user_prompt:
    raise RuntimeError("Prompt đang trống.")


# =========================================================
# 2. CHARACTER LOCK
# =========================================================

miu = characters["characters"]["miu"]
bong = characters["characters"]["bong"]

CHARACTER_LOCK = f"""
CHAR_01 — Miu:
{miu.get("description", "")}

Miu must have:
- small round fox kit body
- bright orange fur
- pure white belly
- white-tipped tail
- big round expressive eyes
- large fluffy ears with white fur tips
- two small white fur streaks on both cheeks
- pastel sky-blue scarf with small white polka dots
- child-like proportions
- extremely cute 3D animated movie appearance

CHAR_02 — Bống:
{bong.get("description", "")}

Bống must have:
- small rabbit kit body
- cream-white fur
- long upright ears
- pale pink inner ears
- left ear slightly drooping
- pale butter-yellow overall
- small pale pink flower behind the left ear
- child-like proportions
- soft and gentle 3D animated movie appearance

STRICT CHARACTER CONSISTENCY:
Do not redesign either character.
Do not change fur colors.
Do not change clothes.
Do not change accessories.
Do not change proportions.
Do not invent additional versions of the characters.
"""


# =========================================================
# 3. TẠO KỊCH BẢN 24 CẢNH
# =========================================================

# Vì chưa có LLM riêng, ta tạo cấu trúc cảnh từ prompt.
# Sau này có thể thay phần này bằng một LLM API.

scene_templates = [
    "Mở đầu câu chuyện và giới thiệu địa điểm.",
    "Miu và Bống xuất hiện cùng nhau.",
    "Hai bạn phát hiện một điều bất thường.",
    "Miu tò mò tiến lại gần.",
    "Bống phát hiện ra vấn đề.",
    "Hai bạn nói chuyện với nhau.",
    "Hai bạn quyết định giúp đỡ.",
    "Miu đưa ra ý tưởng đầu tiên.",
    "Bống thử thực hiện ý tưởng.",
    "Một khó khăn bất ngờ xuất hiện.",
    "Miu cố gắng giải quyết.",
    "Bống tìm ra một cách khác.",
    "Hai bạn cùng phối hợp.",
    "Vấn đề trở nên khó khăn hơn.",
    "Miu và Bống không bỏ cuộc.",
    "Hai bạn tìm được manh mối.",
    "Cả hai cùng thực hiện kế hoạch.",
    "Mọi chuyện bắt đầu tốt đẹp.",
    "Một khoảnh khắc vui vẻ xảy ra.",
    "Vấn đề gần như được giải quyết.",
    "Miu và Bống hoàn thành nhiệm vụ.",
    "Những người bạn xung quanh vui mừng.",
    "Miu và Bống cùng nhìn lại cuộc phiêu lưu.",
    "Kết thúc vui vẻ và tích cực."
]


scenes = []

for i, template in enumerate(scene_templates, 1):
    scenes.append({
        "number": i,
        "description": f"""
Story idea:
{user_prompt}

Scene instruction:
{template}

The scene must contain characters and events appropriate
for a children's 3D animated story.
"""
    })


# =========================================================
# 4. TẠO PROMPT ẢNH
# =========================================================

def make_image_prompt(scene):
    return f"""
Create a single vertical 9:16 frame from a children's
3D animated movie.

STORY:
{user_prompt}

SCENE:
{scene["description"]}

CHARACTER LOCK:
{CHARACTER_LOCK}

VISUAL STYLE:
- high quality 3D animated movie
- cute children's animation
- soft pastel colors
- cinematic lighting
- soft global illumination
- detailed fluffy fur
- expressive faces
- child friendly
- warm and positive
- vertical composition
- 9:16

IMPORTANT:
The characters must remain visually identical to their
defined character designs.
Never redesign Miu or Bống.
Never replace them with different animals.
Do not add text, subtitles, logos or watermarks.
"""


# =========================================================
# 5. GỌI HUGGING FACE / FLUX
# =========================================================

API_URL = (
    "https://router.huggingface.co/"
    "fal-ai/fal-ai/flux/schnell"
)

headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}


def generate_image(prompt, filename):

    response = requests.post(
        API_URL,
        headers=headers,
        json={
            "prompt": prompt
        },
        timeout=180
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"FLUX API lỗi {response.status_code}: "
            f"{response.text[:1000]}"
        )

    content_type = response.headers.get(
        "content-type",
        ""
    )

    # -----------------------------------------
    # Trường hợp API trả trực tiếp ảnh
    # -----------------------------------------

    if "image" in content_type:
        with open(filename, "wb") as f:
            f.write(response.content)

        return

    # -----------------------------------------
    # Trường hợp API trả JSON
    # -----------------------------------------

    try:
        data = response.json()
    except Exception:
        raise RuntimeError(
            "API không trả về ảnh hoặc JSON hợp lệ."
        )

    image_url = None

    if isinstance(data, dict):

        image_url = (
            data.get("image")
            or data.get("url")
        )

        if not image_url and "images" in data:
            images = data["images"]

            if isinstance(images, list) and images:
                first = images[0]

                if isinstance(first, str):
                    image_url = first

                elif isinstance(first, dict):
                    image_url = (
                        first.get("url")
                        or first.get("image")
                    )

    elif isinstance(data, list) and data:

        first = data[0]

        if isinstance(first, str):
            image_url = first

        elif isinstance(first, dict):
            image_url = (
                first.get("url")
                or first.get("image")
            )

    if not image_url:
        raise RuntimeError(
            "Không tìm thấy URL ảnh trong phản hồi API:\n"
            + str(data)[:2000]
        )

    image_response = requests.get(
        image_url,
        timeout=180
    )

    image_response.raise_for_status()

    with open(filename, "wb") as f:
        f.write(image_response.content)


# =========================================================
# 6. TẠO 24 FRAME
# =========================================================

print("====================================")
print("AI VIDEO MAKER")
print("Đang tạo 24 cảnh...")
print("====================================")

for scene in scenes:

    number = scene["number"]

    filename = f"frame{number}.png"

    print(
        f"[{number}/24] Đang tạo cảnh..."
    )

    prompt = make_image_prompt(scene)

    generate_image(
        prompt,
        filename
    )

    print(
        f"[{number}/24] Đã tạo {filename}"
    )


# =========================================================
# 7. TẠO LỜI THOẠI TIẾNG VIỆT
# =========================================================

voice_lines = [
    f"Hôm nay, Miu và Bống bắt đầu một cuộc phiêu lưu mới: {user_prompt}.",
    "Hai người bạn cùng nhau khám phá mọi điều thú vị xung quanh.",
    "Bỗng nhiên, họ phát hiện ra một điều rất bất ngờ.",
    "Miu tò mò tiến lại gần để xem chuyện gì đang xảy ra.",
    "Bống cũng nhanh chóng đến bên cạnh người bạn của mình.",
    "Hai bạn quyết định cùng nhau tìm cách giải quyết vấn đề.",
    "Miu nghĩ ra một ý tưởng thật hay.",
    "Bống vui vẻ đồng ý và bắt đầu giúp Miu.",
    "Nhưng mọi chuyện không dễ dàng như hai bạn nghĩ.",
    "Một khó khăn mới bất ngờ xuất hiện.",
    "Miu và Bống vẫn không bỏ cuộc.",
    "Hai bạn cùng suy nghĩ và tìm ra một cách khác.",
    "Lần này, mọi việc bắt đầu tiến triển tốt hơn.",
    "Hai người bạn phối hợp thật ăn ý.",
    "Cuối cùng, điều kỳ diệu cũng xảy ra.",
    "Miu và Bống đã hoàn thành nhiệm vụ.",
    "Hai bạn nhìn nhau và cùng mỉm cười thật vui.",
    "Qua cuộc phiêu lưu này, họ hiểu rằng giúp đỡ nhau luôn là điều tuyệt vời.",
    "Và quan trọng nhất, không nên bỏ cuộc khi gặp khó khăn.",
    "Miu và Bống rất vui vì đã cùng nhau làm được điều tốt.",
    "Cuộc phiêu lưu hôm nay kết thúc thật hạnh phúc.",
    "Những người bạn xung quanh cũng vui mừng.",
    "Miu và Bống cùng chào tạm biệt mọi người.",
    "Hẹn gặp lại các bạn trong cuộc phiêu lưu tiếp theo!"
]


voice_text = " ".join(voice_lines)


# =========================================================
# 8. EDGE TTS
# =========================================================

async def create_voice():

    print("Đang tạo giọng tiếng Việt...")

    voice = edge_tts.Communicate(
        voice_text,
        "vi-VN-HoaiMyNeural",
        rate="+0%",
        volume="+0%"
    )

    await voice.save("voice.mp3")

    print("Đã tạo voice.mp3")


asyncio.run(create_voice())


# =========================================================
# 9. KIỂM TRA FILE
# =========================================================

for i in range(1, 25):

    filename = Path(
        f"frame{i}.png"
    )

    if not filename.exists():
        raise RuntimeError(
            f"Thiếu {filename}"
        )

voice_file = Path("voice.mp3")

if not voice_file.exists():
    raise RuntimeError(
        "Không tạo được voice.mp3"
    )


print("====================================")
print("HOÀN TẤT RENDER")
print("24 ảnh + voice.mp3 đã được tạo.")
print("FFmpeg sẽ ghép thành output.mp4.")
print("Không có nhạc nền.")
print("====================================")
