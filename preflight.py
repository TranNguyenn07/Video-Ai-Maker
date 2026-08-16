import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent

CHAR_DIR = ROOT / "assets" / "characters"
STORY = ROOT / "assets" / "story.json"

MIN_SCENES = 12
MAX_SCENES = 18
MIN_DURATION = 60
MAX_DURATION = 90


def fail(message):
    print("\n" + "=" * 70)
    print("PREFLIGHT FAILED")
    print("=" * 70)
    print(message)
    print("=" * 70)
    sys.exit(1)


def ok(message):
    print("[OK]", message)


def command_exists(name):
    return shutil.which(name) is not None


def check_command(name):
    if not command_exists(name):
        fail(f"Thiếu command: {name}")
    ok(f"{name} available")


def check_image(path, name):
    if not path.exists():
        fail(f"Thiếu {name}: {path}")

    if path.stat().st_size < 10_000:
        fail(
            f"{name} quá nhỏ: "
            f"{path.stat().st_size} bytes"
        )

    try:
        with Image.open(path) as img:
            img.verify()
    except Exception as exc:
        fail(f"{name} không phải ảnh hợp lệ: {exc}")

    with Image.open(path) as img:
        width, height = img.size

    if width < 512 or height < 512:
        fail(
            f"{name} quá nhỏ: "
            f"{width}x{height}"
        )

    ok(
        f"{name}: {width}x{height}, "
        f"{path.stat().st_size} bytes"
    )


def main():
    print("=" * 70)
    print("AI VIDEO MAKER PREFLIGHT")
    print("=" * 70)

    # --------------------------------------------------------
    # Python
    # --------------------------------------------------------

    if sys.version_info < (3, 10):
        fail(
            f"Python quá cũ: {sys.version}"
        )

    ok(f"Python {sys.version.split()[0]}")

    # --------------------------------------------------------
    # Commands
    # --------------------------------------------------------

    check_command("ffmpeg")
    check_command("ffprobe")

    # --------------------------------------------------------
    # API key
    # --------------------------------------------------------

    if not os.environ.get("OPENAI_API_KEY", "").strip():
        fail(
            "OPENAI_API_KEY chưa được thiết lập."
        )

    ok("OPENAI_API_KEY exists")

    # --------------------------------------------------------
    # Character references
    # --------------------------------------------------------

    check_image(
        CHAR_DIR / "miu.png",
        "Miu reference"
    )

    check_image(
        CHAR_DIR / "bong.png",
        "Bong reference"
    )

    # --------------------------------------------------------
    # Character JSON
    # --------------------------------------------------------

    characters_json = CHAR_DIR / "characters.json"

    if not characters_json.exists():
        fail(
            f"Thiếu {characters_json}"
        )

    try:
        with open(
            characters_json,
            "r",
            encoding="utf-8"
        ) as f:
            characters = json.load(f)
    except Exception as exc:
        fail(
            f"characters.json lỗi: {exc}"
        )

    for char_id in ("CHAR_01", "CHAR_02"):
        if char_id not in characters:
            fail(
                f"Thiếu {char_id} trong characters.json"
            )

    ok("Character configuration valid")

    # --------------------------------------------------------
    # Story
    # --------------------------------------------------------

    if not STORY.exists():
        fail(
            f"Thiếu story: {STORY}"
        )

    try:
        with open(
            STORY,
            "r",
            encoding="utf-8"
        ) as f:
            story = json.load(f)
    except Exception as exc:
        fail(
            f"story.json lỗi: {exc}"
        )

    scenes = story.get("scenes")

    if not isinstance(scenes, list):
        fail(
            "story.json phải có scenes[]"
        )

    scene_count = len(scenes)

    if not (
        MIN_SCENES
        <= scene_count
        <= MAX_SCENES
    ):
        fail(
            f"Số cảnh hiện tại: {scene_count}. "
            f"Phải nằm trong {MIN_SCENES}-{MAX_SCENES}."
        )

    ok(
        f"Scene count: {scene_count}"
    )

    # --------------------------------------------------------
    # Scene text
    # --------------------------------------------------------

    for index, scene in enumerate(
        scenes,
        start=1
    ):
        if not scene.get("description", "").strip():
            fail(
                f"Cảnh {index} thiếu description"
            )

        if not scene.get("narrator", "").strip():
            fail(
                f"Cảnh {index} thiếu narrator"
            )

        if "miu" not in scene:
            fail(
                f"Cảnh {index} thiếu miu"
            )

        if "bong" not in scene:
            fail(
                f"Cảnh {index} thiếu bong"
            )

    ok("All scenes contain valid text")

    # --------------------------------------------------------
    # Duration estimate
    # --------------------------------------------------------

    # 5 seconds is the baseline.
    # The final renderer adjusts based on actual TTS duration.
    estimated = scene_count * 5

    if estimated < MIN_DURATION:
        fail(
            f"Ước lượng thời lượng {estimated}s < 60s. "
            "Thêm cảnh hoặc nội dung thoại."
        )

    if estimated > MAX_DURATION:
        fail(
            f"Ước lượng thời lượng {estimated}s > 90s. "
            "Giảm số cảnh hoặc thoại."
        )

    ok(
        f"Estimated duration: "
        f"{estimated}s"
    )

    # --------------------------------------------------------
    # Directories
    # --------------------------------------------------------

    for directory in (
        ROOT / "cache",
        ROOT / "cache" / "images",
        ROOT / "cache" / "tts",
        ROOT / "output"
    ):
        directory.mkdir(
            parents=True,
            exist_ok=True
        )

    ok("Output/cache directories ready")

    print("")
    print("=" * 70)
    print("PREFLIGHT PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()
