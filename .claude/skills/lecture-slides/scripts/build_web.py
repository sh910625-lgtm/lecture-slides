"""웹 배포용 미디어 복사: lectures/N강의 사진·영상·포스터를 docs/lectureN/assets/로 모은다.

사용:  python build_web.py lectures/1강 docs/lecture1
       → images/*.jpg, animations/*.mp4, animations/*.png 를 <out>/assets/ 로 복사 (바뀐 파일만)
       + 놀이터의 'manim 코드 보기'용으로 scenes.py, manim_style.py 도 함께 복사
"""
import glob
import os
import shutil
import sys


def main(lecture_dir, out_dir):
    dst = os.path.join(out_dir, "assets")
    os.makedirs(dst, exist_ok=True)
    srcs = (glob.glob(os.path.join(lecture_dir, "images", "*.jpg"))
            + glob.glob(os.path.join(lecture_dir, "animations", "*.mp4"))
            + glob.glob(os.path.join(lecture_dir, "animations", "*.png"))
            + glob.glob(os.path.join(lecture_dir, "animations", "scenes.py"))
            + [os.path.join(os.path.dirname(os.path.abspath(__file__)), "manim_style.py")])
    for f in sorted(srcs):
        t = os.path.join(dst, os.path.basename(f))
        if not os.path.exists(t) or os.path.getmtime(t) < os.path.getmtime(f):
            shutil.copy2(f, t)
            print("copied", os.path.basename(f))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main(*sys.argv[1:3])
