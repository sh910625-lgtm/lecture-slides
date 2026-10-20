"""비유 사진 찾기 (Wikimedia Commons, 재사용 가능한 라이선스만).

1) 후보 검색 → 썸네일 + 한눈에 보기 시트
   python find_images.py search <작업폴더> vending="vending machine" pizza="whole pizza"
   → <작업폴더>/candidates.json, <작업폴더>/key_i.jpg, <작업폴더>/sheet_1.png ...
   시트를 Read로 보고 고른다.

2) 고른 사진 내려받기 (+ credits.json, 출처.md 갱신)
   python find_images.py fetch <작업폴더> <images폴더> vending=vending_0 pizza=pizza_2
   → <images폴더>/vending.jpg ...

라이선스: CC0, Public domain, CC BY, CC BY-SA 만 통과 (NC/ND 제외).
요청 헤더에 개인정보(이메일 등)를 넣지 않는다.
"""
import io
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

from PIL import Image, ImageDraw

UA = {"User-Agent": "lecture-slides/1.0 (classroom slides)"}
API = "https://commons.wikimedia.org/w/api.php?"
OK_LICENSE = re.compile(r"^(CC0|Public domain|PD|CC BY(-SA)? [\d.]+|CC BY(-SA)?)\b", re.I)
BAD_LICENSE = re.compile(r"NC|ND", re.I)


def _get(url, tries=4):
    for a in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
        except Exception as e:  # 429 등은 잠시 쉬고 재시도
            if a == tries - 1:
                raise
            time.sleep(5 if "429" in str(e) else 1.5)


def _clean(html):
    return re.sub(r"\s+", " ", re.sub("<[^>]+>", "", html or "")).strip()


def search(work, queries, per=8, min_width=800):
    os.makedirs(work, exist_ok=True)
    cpath = os.path.join(work, "candidates.json")
    cands = json.load(open(cpath, encoding="utf-8")) if os.path.exists(cpath) else {}
    for key, q in queries.items():
        params = {"action": "query", "format": "json", "generator": "search", "gsrnamespace": 6,
                  "gsrsearch": f"{q} filetype:bitmap", "gsrlimit": 30, "prop": "imageinfo",
                  "iiprop": "url|extmetadata|size", "iiurlwidth": 640}
        data = json.loads(_get(API + urllib.parse.urlencode(params)))
        items = []
        for p in sorted(data.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 0)):
            ii = p["imageinfo"][0]
            m = ii.get("extmetadata", {})
            lic = _clean(m.get("LicenseShortName", {}).get("value", ""))
            if not OK_LICENSE.search(lic) or BAD_LICENSE.search(lic) or ii["width"] < min_width:
                continue
            items.append({"title": p["title"].removeprefix("File:").rsplit(".", 1)[0],
                          "creator": _clean(m.get("Artist", {}).get("value", "")) or "unknown",
                          "license": lic, "url": ii["url"], "thumb": ii["thumburl"],
                          "landing": ii["descriptionurl"], "w": ii["width"], "h": ii["height"]})
            if len(items) == per:
                break
        cands[key] = items
        for i, c in enumerate(items):
            try:
                Image.open(io.BytesIO(_get(c["thumb"]))).convert("RGB").save(
                    os.path.join(work, f"{key}_{i}.jpg"), quality=88)
            except Exception as e:
                print(f"  {key}_{i} 썸네일 실패: {str(e)[:60]}")
            time.sleep(0.3)
        print(f"{key}: {len(items)}개 ({q})")
    json.dump(cands, open(cpath, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    sheets(work, list(queries))


def sheets(work, keys, per_sheet=4):
    W, H = 240, 170
    for n in range(0, len(keys), per_sheet):
        ks = keys[n:n + per_sheet]
        sh = Image.new("RGB", (8 * W, len(ks) * H), "white")
        d = ImageDraw.Draw(sh)
        for r, k in enumerate(ks):
            for i in range(8):
                p = os.path.join(work, f"{k}_{i}.jpg")
                if os.path.exists(p):
                    im = Image.open(p)
                    im.thumbnail((W - 6, H - 6))
                    sh.paste(im, (i * W + 3, r * H + 3))
                    d.rectangle([i * W + 3, r * H + 3, i * W + 100, r * H + 18], fill="red")
                    d.text((i * W + 6, r * H + 5), f"{k}_{i}", fill="white")
        out = os.path.join(work, f"sheet_{n // per_sheet + 1}.png")
        sh.save(out)
        print("시트:", out)


def fetch(work, img_dir, picks):
    cands = json.load(open(os.path.join(work, "candidates.json"), encoding="utf-8"))
    os.makedirs(img_dir, exist_ok=True)
    cpath = os.path.join(img_dir, "credits.json")
    credits = json.load(open(cpath, encoding="utf-8")) if os.path.exists(cpath) else {}
    for name, ref in picks.items():
        key, i = ref.rsplit("_", 1)
        c = cands[key][int(i)]
        url = c["thumb"].replace("/640px-", "/1280px-") if c["w"] > 1280 else c["url"]
        im = Image.open(io.BytesIO(_get(url))).convert("RGB")
        im.thumbnail((1600, 1600))
        im.save(os.path.join(img_dir, name + ".jpg"), quality=88)
        short = re.sub(r"^(Photographie personnelle\s*)?User:", "", c["creator"]).split(",")[0].strip()[:40]
        credits[name] = {"title": c["title"][:80], "creator": c["creator"], "creator_short": short,
                         "license": c["license"], "url": c["landing"]}
        print(f"{name}.jpg ← {c['title'][:50]} / {short} / {c['license']}")
        time.sleep(1)
    json.dump(credits, open(cpath, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    with open(os.path.join(img_dir, "출처.md"), "w", encoding="utf-8") as f:
        f.write("# 이미지 출처\n\n| 파일 | 제목 | 저작자 | 라이선스 | 원본 |\n|---|---|---|---|---|\n")
        for n, v in credits.items():
            f.write(f"| {n}.jpg | {v['title']} | {v['creator']} | {v['license']} | {v['url']} |\n")


def _pairs(args):
    out = {}
    for a in args:
        k, v = a.split("=", 1)
        out[k] = v
    return out


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    cmd = sys.argv[1]
    if cmd == "search":
        search(sys.argv[2], _pairs(sys.argv[3:]))
    elif cmd == "fetch":
        fetch(sys.argv[2], sys.argv[3], _pairs(sys.argv[4:]))
    else:
        sys.exit(__doc__)
