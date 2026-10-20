"""manim 장면을 1920x1080 30fps 영상 + 마지막 장면 PNG(포스터)로 렌더링.

python render_anims.py lectures/N강/animations/scenes.py [장면 ...]
장면을 생략하면 scenes.py 안의 모든 Scene 클래스를 렌더링한다.
결과: animations/<장면>.mp4, animations/<장면>.png
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

MANIM = os.path.join(os.path.dirname(sys.executable), "manim.exe")


def main():
    scenes_py = os.path.abspath(sys.argv[1])
    out_dir = os.path.dirname(scenes_py)
    names = sys.argv[2:] or re.findall(r"^class (\w+)\(Scene\)", open(scenes_py, encoding="utf-8").read(), re.M)
    media = tempfile.mkdtemp(prefix="manim_")
    stem = os.path.splitext(os.path.basename(scenes_py))[0]
    for n in names:
        base = [MANIM, "-r", "1920,1080", "--media_dir", media, "-v", "ERROR", scenes_py, n]
        v = subprocess.run(base[:3] + ["--fps", "30", "-o", n] + base[3:], capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        s = subprocess.run(base[:3] + ["-s"] + base[3:], capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        mp4 = os.path.join(media, "videos", stem, "1080p30", n + ".mp4")
        if v.returncode or not os.path.exists(mp4):
            print(f"FAIL {n}\n{v.stderr[-1500:]}")
            continue
        shutil.copy(mp4, os.path.join(out_dir, n + ".mp4"))
        pngs = [p for p in os.listdir(os.path.join(media, "images", stem)) if p.startswith(n + "_")] \
            if os.path.isdir(os.path.join(media, "images", stem)) else []
        if s.returncode == 0 and pngs:
            shutil.copy(os.path.join(media, "images", stem, pngs[0]), os.path.join(out_dir, n + ".png"))
        print(f"ok {n}")
    shutil.rmtree(os.path.join(out_dir, "__pycache__"), ignore_errors=True)
    shutil.rmtree(media, ignore_errors=True)


if __name__ == "__main__":
    main()
