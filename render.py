import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import requests
from PIL import Image


ROOT = Path(__file__).resolve().parent

STORY_FILE = ROOT / "assets" / "story.json"
CHAR_FILE = ROOT / "assets" / "characters" / "characters.json"

MIU_REF = ROOT / "assets" / "characters" / "miu.png"
BONG_REF = ROOT / "assets" / "characters" / "bong.png"

CACHE_IMAGES = ROOT / "cache" / "images"
CACHE_TTS = ROOT / "cache" / "tts"

OUTPUT = ROOT / "output"
SCENES = OUTPUT / "scenes"
AUDIO = OUTPUT / "audio"

VIDEO = OUTPUT / "video.mp4"

IMAGE_MODEL = "gpt-image-1"

MIN_SCENES = 12
MAX_SCENES = 18

MIN_VIDEO_SECONDS = 60
MAX_VIDEO_SECONDS = 90

WIDTH = 1080
HEIGHT = 1920

FPS = 30


# ============================================================
# BASIC
# ============================================================

def fail(message):
    print("\n" + "=" * 70)
    print("RENDER FAILED")
    print("=" * 70)
    print(message)
    print("=" * 70)
    sys.exit(1)


def run(command):
    print("$", " ".join(str(x) for x in command))

    result = subprocess.run(
        command,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    print(result.stdout)

    if result.returncode != 0:
        fail(
            "Command failed with exit code "
            f"{result.returncode}"
        )


def require_command(command):
    if shutil.which(command) is None:
        fail(
            f"Không tìm thấy command: {command}"
        )


def load_json(path):
    if not path.exists():
        fail(
            f"Không tìm thấy: {path}"
        )

    try:
        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:
            return json.load(f)
    except Exception as exc:
        fail(
            f"JSON lỗi {path}: {exc}"
        )


def sha256_text(value):
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()

    with open(path, "rb") as f:
        while True:
            chunk = f.read(1024 * 1024)

            if not chunk:
                break

            h.update(chunk)

    return h.hexdigest()


# ============================================================
# IMAGE VALIDATION
# ============================================================

def validate_png(path, label):
    if not path.exists():
        fail(
            f"{label} không tồn tại: {path}"
        )

    if path.stat().st_size < 10_000:
        fail(
            f"{label} quá nhỏ: "
            f"{path.stat().st_size} bytes"
        )

    try:
        with Image.open(path) as img:
            img.verify()
    except Exception as exc:
        fail(
            f"{label} invalid image: {exc}"
        )

    try:
        with Image.open(path) as img:
            width, height = img.size
            img.load()
    except Exception as exc:
        fail(
            f"{label} không thể decode: {exc}"
        )

    if width < 512 or height < 512:
        fail(
            f"{label} quá nhỏ: "
            f"{width}x{height}"
        )

    print(
        f"[OK] {label}: "
        f"{width}x{height}, "
        f"{path.stat().st_size} bytes"
    )


# ============================================================
# IMAGE CACHE
# ============================================================

def image_cache_key(scene):
    data = {
        "model": IMAGE_MODEL,
        "scene": scene,
        "miu_hash": sha256_file(MIU_REF),
        "bong_hash": sha256_file(BONG_REF),
        "version": 3
    }

    raw = json.dumps(
        data,
        ensure_ascii=False,
        sort_keys=True
    )

    return sha256_text(raw)


def generate_image(scene, index):
    key = image_cache_key(scene)

    cache_file = (
        CACHE_IMAGES
        / f"{key}.png"
    )

    output_file = (
        SCENES
        / f"scene_{index:02d}.png"
    )

    # --------------------------------------------------------
    # CACHE HIT
    # --------------------------------------------------------

    if cache_file.exists():
        print(
            f"[CACHE HIT] image scene {index}"
        )

        validate_png(
            cache_file,
            f"cached scene {index}"
        )

        shutil.copy2(
            cache_file,
            output_file
        )

        return output_file

    api_key = os.environ.get(
        "OPENAI_API_KEY",
        ""
    ).strip()

    if not api_key:
        fail(
            "OPENAI_API_KEY chưa có."
        )

    characters = load_json(
        CHAR_FILE
    )

    miu = characters["CHAR_01"]
    bong = characters["CHAR_02"]

    prompt = f"""
Create a high-end vertical 3D animated movie frame.

AUTHORITATIVE CHARACTER REFERENCES:
Two attached images are the canonical visual identity
references.

CHAR_01 — MIU:
{miu["description"]}

IDENTITY LOCK:
{", ".join(miu["identity_lock"])}

CHAR_02 — BỐNG:
{bong["description"]}

IDENTITY LOCK:
{", ".join(bong["identity_lock"])}

ABSOLUTE RULE:
The attached character references are authoritative.
Preserve the same characters. Do not redesign them.

Do not change:
- species
- face
- fur color
- body proportions
- ears
- clothing
- scarf
- flower
- character age
- character identity

STYLE:
premium 3D animated feature film,
cinematic lighting,
detailed soft fur,
beautiful expressive eyes,
high-quality character modeling,
soft global illumination,
natural forest environment,
cinematic depth,
subtle volumetric light,
warm emotional storytelling,
polished professional animation-film look.

SCENE:
{scene["description"]}

CHARACTER ACTION:
Miu and Bống should be clearly visible and naturally
interacting with the scene.

COMPOSITION:
vertical 9:16,
portrait framing,
1080x1920 target,
clear foreground characters,
strong storytelling composition.

STRICT NEGATIVE REQUIREMENTS:
no text,
no subtitles,
no logo,
no watermark,
no UI,
no extra limbs,
no duplicate characters,
no deformed faces,
no realistic animal anatomy,
no character redesign,
no costume changes.
"""

    print("")
    print(
        "=" * 70
    )
    print(
        f"GENERATING IMAGE {index}"
    )
    print(
        "=" * 70
    )

    url = (
        "https://api.openai.com/v1/images/edits"
    )

    headers = {
        "Authorization":
            f"Bearer {api_key}"
    }

    files = [
        (
            "image[]",
            (
                "miu.png",
                open(MIU_REF, "rb"),
                "image/png"
            )
        ),
        (
            "image[]",
            (
                "bong.png",
                open(BONG_REF, "rb"),
                "image/png"
            )
        )
    ]

    data = {
        "model": IMAGE_MODEL,
        "prompt": prompt,
        "size": "1024x1536",
        "quality": "high",
        "output_format": "png",
        "input_fidelity": "high"
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            data=data,
            files=files,
            timeout=900
        )
    finally:
        for item in files:
            item[1][1].close()

    if response.status_code != 200:
        fail(
            "Image API error.\n"
            f"HTTP {response.status_code}\n"
            f"{response.text[:5000]}"
        )

    try:
        payload = response.json()
    except Exception as exc:
        fail(
            f"Image API trả JSON lỗi: {exc}"
        )

    if (
        "data" not in payload
        or not payload["data"]
        or "b64_json"
        not in payload["data"][0]
    ):
        fail(
            "Image API không trả ảnh hợp lệ.\n"
            + json.dumps(
                payload,
                ensure_ascii=False
            )[:5000]
        )

    import base64

    try:
        image_bytes = base64.b64decode(
            payload["data"][0]["b64_json"]
        )
    except Exception as exc:
        fail(
            f"Không decode được ảnh: {exc}"
        )

    temp = SCENES / (
        f".scene_{index:02d}.tmp.png"
    )

    with open(temp, "wb") as f:
        f.write(image_bytes)

    validate_png(
        temp,
        f"generated scene {index}"
    )

    # Normalize to PNG.
    with Image.open(temp) as img:
        img = img.convert("RGB")
        img.save(
            cache_file,
            "PNG",
            optimize=True
        )

    temp.unlink(
        missing_ok=True
    )

    validate_png(
        cache_file,
        f"cached scene {index}"
    )

    shutil.copy2(
        cache_file,
        output_file
    )

    print(
        f"[CACHE SAVED] {cache_file}"
    )

    return output_file


# ============================================================
# TTS
# ============================================================

VOICES = {
    "narrator": {
        "voice": "vi-VN-HoaiMyNeural",
        "rate": "+0%",
        "pitch": "+0Hz"
    },

    "miu": {
        "voice": "vi-VN-HoaiMyNeural",
        "rate": "+8%",
        "pitch": "+12Hz"
    },

    "bong": {
        "voice": "vi-VN-NamMinhNeural",
        "rate": "-3%",
        "pitch": "-8Hz"
    }
}


def tts_key(role, text):
    config = VOICES[role]

    raw = json.dumps(
        {
            "role": role,
            "text": text,
            "voice": config["voice"],
            "rate": config["rate"],
            "pitch": config["pitch"],
            "version": 2
        },
        ensure_ascii=False,
        sort_keys=True
    )

    return sha256_text(raw)


def make_tts(role, text):
    text = text.strip()

    if not text:
        return None

    key = tts_key(
        role,
        text
    )

    output = (
        CACHE_TTS
        / f"{key}.mp3"
    )

    if output.exists():
        print(
            f"[CACHE HIT] TTS {role}"
        )

        if output.stat().st_size > 1000:
            return output

        output.unlink()

    config = VOICES[role]

    print(
        f"[TTS] {role}: {text}"
    )

    run([
        sys.executable,
        "-m",
        "edge_tts",
        "--voice",
        config["voice"],
        "--rate",
        config["rate"],
        "--pitch",
        config["pitch"],
        "--text",
        text,
        "--write-media",
        str(output)
    ])

    if (
        not output.exists()
        or output.stat().st_size < 1000
    ):
        fail(
            f"TTS thất bại: {output}"
        )

    return output


# ============================================================
# AUDIO
# ============================================================

def probe_duration(path):
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path)
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        fail(
            f"ffprobe audio failed: "
            f"{result.stderr}"
        )

    try:
        return float(
            result.stdout.strip()
        )
    except Exception:
        fail(
            f"Invalid duration: {path}"
        )


def make_scene_audio(scene, index):
    files = []

    for role in (
        "narrator",
        "miu",
        "bong"
    ):
        text = scene.get(
            role,
            ""
        ).strip()

        if text:
            path = make_tts(
                role,
                text
            )

            if path:
                files.append(
                    path
                )

    if not files:
        fail(
            f"Cảnh {index} không có audio."
        )

    output = (
        AUDIO
        / f"scene_{index:02d}.wav"
    )

    inputs = []

    for path in files:
        inputs.extend(
            [
                "-i",
                str(path)
            ]
        )

    labels = []

    for i in range(len(files)):
        labels.append(
            f"[{i}:a]"
        )

    filter_complex = (
        "".join(labels)
        + f"concat=n={len(files)}:v=0:a=1,"
        "loudnorm=I=-16:TP=-1.5:LRA=11,"
        "aresample=48000,"
        "aformat=channel_layouts=stereo"
        "[a]"
    )

    run([
        "ffmpeg",
        "-y",
        *inputs,
        "-filter_complex",
        filter_complex,
        "-map",
        "[a]",
        "-c:a",
        "pcm_s16le",
        str(output)
    ])

    duration = probe_duration(
        output
    )

    print(
        f"[OK] Scene {index} audio: "
        f"{duration:.2f}s"
    )

    return output, duration


# ============================================================
# VIDEO BUILD
# ============================================================

def build_video(
    scene_files,
    audio_files,
    scene_durations
):
    concat_file = (
        OUTPUT / "scenes.txt"
    )

    with open(
        concat_file,
        "w",
        encoding="utf-8"
    ) as f:
        for path, duration in zip(
            scene_files,
            scene_durations
        ):
            safe = (
                str(path)
                .replace("\\", "/")
                .replace("'", "'\\''")
            )

            f.write(
                f"file '{safe}'\n"
            )

            f.write(
                f"duration {duration:.3f}\n"
            )

        # FFmpeg concat demuxer requires the
        # final file repeated to preserve duration.
        if scene_files:
            last = (
                str(scene_files[-1])
                .replace("\\", "/")
                .replace("'", "'\\''")
            )

            f.write(
                f"file '{last}'\n"
            )

    audio_concat = (
        OUTPUT / "audio.txt"
    )

    with open(
        audio_concat,
        "w",
        encoding="utf-8"
    ) as f:
        for path in audio_files:
            safe = (
                str(path)
                .replace("\\", "/")
                .replace("'", "'\\''")
            )

            f.write(
                f"file '{safe}'\n"
            )

    combined_audio = (
        OUTPUT / "combined_audio.wav"
    )

    run([
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(audio_concat),
        "-ar",
        "48000",
        "-ac",
        "2",
        "-c:a",
        "pcm_s16le",
        str(combined_audio)
    ])

    run([
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_file),
        "-i",
        str(combined_audio),
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-vf",
        (
            f"scale={WIDTH}:{HEIGHT}:"
            "force_original_aspect_ratio=decrease,"
            f"pad={WIDTH}:{HEIGHT}:"
            "(ow-iw)/2:(oh-ih)/2,"
            "format=yuv420p"
        ),
        "-r",
        str(FPS),
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "20",
        "-c:a",
        "aac",
        "-b:a",
        "160k",
        "-ar",
        "48000",
        "-movflags",
        "+faststart",
        "-shortest",
        str(VIDEO)
    ])

    if not VIDEO.exists():
        fail(
            "video.mp4 không được tạo."
        )

    if VIDEO.stat().st_size < 100_000:
        fail(
            "video.mp4 quá nhỏ."
        )


# ============================================================
# FINAL VALIDATION
# ============================================================

def validate_video():
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-show_entries",
            "stream=codec_type",
            "-of",
            "json",
            str(VIDEO)
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        fail(
            f"Final ffprobe failed:\n"
            f"{result.stderr}"
        )

    try:
        data = json.loads(
            result.stdout
        )
    except Exception as exc:
        fail(
            f"Không parse ffprobe: {exc}"
        )

    duration = float(
        data["format"]["duration"]
    )

    stream_types = {
        x["codec_type"]
        for x in data.get(
            "streams",
            []
        )
    }

    print("")
    print(
        "=" * 70
    )
    print(
        f"FINAL VIDEO: {duration:.2f}s"
    )
    print(
        f"STREAMS: {sorted(stream_types)}"
    )
    print(
        "=" * 70
    )

    if duration < MIN_VIDEO_SECONDS:
        fail(
            f"Video chỉ {duration:.2f}s "
            f"< {MIN_VIDEO_SECONDS}s"
        )

    if duration > MAX_VIDEO_SECONDS + 2:
        fail(
            f"Video {duration:.2f}s "
            f"> {MAX_VIDEO_SECONDS}s"
        )

    if "video" not in stream_types:
        fail(
            "Video stream missing."
        )

    if "audio" not in stream_types:
        fail(
            "Audio stream missing."
        )

    print(
        "[SUCCESS] Video contains video + audio."
    )


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("AI VIDEO MAKER")
    print("=" * 70)

    require_command("ffmpeg")
    require_command("ffprobe")

    for directory in (
        CACHE_IMAGES,
        CACHE_TTS,
        OUTPUT,
        SCENES,
        AUDIO
    ):
        directory.mkdir(
            parents=True,
            exist_ok=True
        )

    # --------------------------------------------------------
    # Load story
    # --------------------------------------------------------

    story = load_json(
        STORY_FILE
    )

    scenes = story.get(
        "scenes",
        []
    )

    count = len(scenes)

    if not (
        MIN_SCENES
        <= count
        <= MAX_SCENES
    ):
        fail(
            f"Story có {count} cảnh. "
            f"Phải có {MIN_SCENES}-{MAX_SCENES}."
        )

    print(
        f"Scene count: {count}"
    )

    # --------------------------------------------------------
    # References
    # --------------------------------------------------------

    validate_png(
        MIU_REF,
        "Miu reference"
    )

    validate_png(
        BONG_REF,
        "Bong reference"
    )

    # --------------------------------------------------------
    # Generate images
    # --------------------------------------------------------

    scene_images = []

    for index, scene in enumerate(
        scenes,
        start=1
    ):
        path = generate_image(
            scene,
            index
        )

        scene_images.append(
            path
        )

    # --------------------------------------------------------
    # Generate audio
    # --------------------------------------------------------

    audio_files = []
    scene_durations = []

    for index, scene in enumerate(
        scenes,
        start=1
    ):
        audio, duration = (
            make_scene_audio(
                scene,
                index
            )
        )

        audio_files.append(
            audio
        )

        scene_durations.append(
            duration
        )

    # --------------------------------------------------------
    # Total duration
    # --------------------------------------------------------

    total = sum(
        scene_durations
    )

    print(
        f"Raw audio duration: "
        f"{total:.2f}s"
    )

    # If too short, slow speech slightly is preferable
    # to producing a sub-60-second video.
    if total < MIN_VIDEO_SECONDS:
        fail(
            f"Tổng audio chỉ {total:.2f}s. "
            "Hãy thêm nội dung thoại vào story.json "
            "để video đạt tối thiểu 60 giây."
        )

    if total > MAX_VIDEO_SECONDS:
        fail(
            f"Tổng audio {total:.2f}s > 90s. "
            "Hãy giảm nội dung thoại hoặc số cảnh."
        )

    # --------------------------------------------------------
    # Build
    # --------------------------------------------------------

    build_video(
        scene_images,
        audio_files,
        scene_durations
    )

    # --------------------------------------------------------
    # Final
    # --------------------------------------------------------

    validate_video()

    print("")
    print("=" * 70)
    print("RENDER COMPLETE")
    print("=" * 70)
    print(
        f"Video: {VIDEO}"
    )
    print(
        f"Size: {VIDEO.stat().st_size} bytes"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()
