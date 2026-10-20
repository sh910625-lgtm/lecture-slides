"""결과 확인용 미리보기.

슬라이드:  python preview.py slides <pptx> <작업폴더>
           → PowerPoint로 PNG를 뽑아 6장씩 묶은 <작업폴더>/deck_1.png ... (Read로 확인)
영상:      python preview.py frames <animations폴더> <작업폴더>
           → 각 영상의 30% / 55% / 80% / 마지막 장면을 모은 <작업폴더>/frames.png
"""
import glob
import os
import re
import subprocess
import sys

from PIL import Image, ImageDraw

PS = r"""param($in,$out)
if (Test-Path $out) { Remove-Item -Recurse -Force $out }
New-Item -ItemType Directory -Force $out | Out-Null
$app = New-Object -ComObject PowerPoint.Application
$p = $app.Presentations.Open($in, $true, $false, $false)
$p.SaveAs($out, 18)
$p.Close(); $app.Quit()
"""


def slides(pptx, work):
    os.makedirs(work, exist_ok=True)
    ps1 = os.path.join(work, "_export.ps1")
    open(ps1, "w", encoding="utf-8-sig").write(PS)
    out = os.path.normpath(os.path.abspath(os.path.join(work, "png")))   # PowerPoint는 '\' 경로만 받는다
    subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ps1,
                    os.path.normpath(os.path.abspath(pptx)), out], check=True)
    fs = sorted(glob.glob(os.path.join(out, "*.PNG")), key=lambda f: int(re.findall(r"\d+", os.path.basename(f))[-1]))
    W, H = 960, 540
    for n in range(0, len(fs), 6):
        sub = fs[n:n + 6]
        sh = Image.new("RGB", (2 * W, ((len(sub) + 1) // 2) * H), "white")
        d = ImageDraw.Draw(sh)
        for i, f in enumerate(sub):
            x, y = (i % 2) * W, (i // 2) * H
            sh.paste(Image.open(f).convert("RGB").resize((W - 6, H - 6)), (x + 3, y + 3))
            d.rectangle([x + 3, y + 3, x + 40, y + 25], fill="red")
            d.text((x + 8, y + 8), str(n + i + 1), fill="white")
        p = os.path.join(work, f"deck_{n // 6 + 1}.png")
        sh.save(p)
        print(p)


def frames(anim_dir, work):
    import av
    os.makedirs(work, exist_ok=True)
    vids = sorted(glob.glob(os.path.join(anim_dir, "*.mp4")))
    W, H = 480, 270
    sh = Image.new("RGB", (4 * W, len(vids) * H), "white")
    d = ImageDraw.Draw(sh)
    for r, v in enumerate(vids):
        c = av.open(v)
        fr = [f.to_image() for f in c.decode(c.streams.video[0])]
        print(f"{os.path.basename(v)}: {len(fr) / 30:.1f}s")
        for j, t in enumerate((0.3, 0.55, 0.8, 1.0)):
            sh.paste(fr[min(int(len(fr) * t), len(fr) - 1)].resize((W - 4, H - 4)), (j * W + 2, r * H + 2))
        d.text((6, r * H + 6), os.path.basename(v), fill="red")
    p = os.path.join(work, "frames.png")
    sh.save(p)
    print(p)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    {"slides": slides, "frames": frames}[sys.argv[1]](*sys.argv[2:4])
