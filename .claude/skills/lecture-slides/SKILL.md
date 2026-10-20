---
name: lecture-slides
description: 이 프로젝트의 강의자료(PPT)를 만든다 - 교재(references/)를 읽고, manim 애니메이션과 인터넷에서 찾은 비유 사진을 넣어 템플릿 디자인으로 lectures/N강/에 pptx를 만든다. "N강 만들어줘", "강의자료 만들어줘", "슬라이드 만들어줘", 기존 강의 수정 요청에 사용.
---

# 강의자료 만들기

결과물: `lectures/N강/N강_<주제>.pptx` (영상 자동 재생, 발표자 노트, 이미지 출처 포함)

```
lectures/N강/
├── N강_<주제>.pptx
├── build_slides.py          ← 슬라이드 내용 (slidekit 사용)
├── animations/scenes.py     ← manim 장면 → <장면>.mp4 + <장면>.png(포스터)
└── images/                  ← 비유 사진 + credits.json + 출처.md
```

도구 (모두 `scripts/`, Python은 `C:/Users/KDP/.venvs/manim/Scripts/python.exe -X utf8`로 실행):

| 파일 | 하는 일 |
|---|---|
| `slidekit.py` | 템플릿 표지·마무리 유지, 제목/부제/바닥글/노트가 붙은 슬라이드, `text` `box` `circle_num` `table` `numbered_cards` `picture` `video` `analogy_tag`, 출처 슬라이드, 저장 + 자동 재생 |
| `manim_style.py` | 템플릿과 같은 색, `T()`(Pretendard 텍스트), `plain_axes` `bar` `bar_chart` `x_labels` |
| `render_anims.py` | scenes.py의 장면을 1920x1080 30fps mp4 + 마지막 장면 png로 렌더링 |
| `find_images.py` | Wikimedia Commons에서 재사용 가능 라이선스 사진 검색(`search`) → 고른 사진 내려받기(`fetch`) |
| `preview.py` | `slides`: PowerPoint로 렌더링한 슬라이드 묶음 이미지 / `frames`: 영상 중간 장면 묶음 |
| `autoplay.ps1` | 영상을 "슬라이드 열리면 자동 재생"으로 (Deck.save가 자동 호출) |

예시 전체 구현: `lectures/1강/` (build_slides.py, animations/scenes.py). 새 강의는 이것을 복사해 고치는 것이 가장 빠르다.

## 순서

### 1. 내용 파악
- `CLAUDE.md`, `lectures/강의개요.md`, `lectures/차시별_목차.md`, `style/스타일가이드.md`를 읽는다 (빈칸이면 교재 기준으로 정하고 마지막에 알린다).
- 교재 PDF는 `pymupdf`로 텍스트를 뽑는다. **수식 글자는 깨져 나오므로** 흐름·개념·예시 상황만 가져오고, 숫자가 필요한 예제는 직접 만들어 검산한다. 쪽 범위는 "학습 목표" 줄로 절을 나눠 찾는다.

### 2. 구성 (보통 16~20장)
표지 → 학습 목표(+흐름) → 생각 열기(사진) → [개념 → 애니메이션 → **비유**]를 개념마다 반복 → 예제(애니메이션 + 풀이) → 성질/정리 → 확인 문제 → 정답과 정리 → 이미지 출처 → 마무리.
- 핵심 개념마다 비유 1개 이상. 좋은 비유는 "구조가 같은 일상 사물"이다 (1강 예: 확률변수=자판기, 합=1은 피자 한 판, 이산/연속=계단/경사로, 질량/밀도=저울 추/모래 더미). 비유 슬라이드엔 대응표나 두 사진 비교를 쓰고 `analogy_tag`를 붙인다.
- 모든 슬라이드에 발표자 노트(무엇을 짚을지, 영상에서 볼 것).

### 3. 애니메이션 (manim)
- `animations/scenes.py`에 장면 클래스 작성, 맨 위에서 `manim_style`을 import (1강 파일 참고). 장면당 10~15초, 마지막 장면이 그대로 포스터가 되므로 **최종 상태가 핵심 결론**이 되게 끝낸다.
- 그래프·도식·변화가 있는 개념에 쓴다: 대응(화살표), 막대 자라기/쌓기, 막대→곡선, 넓이 채우기(ValueTracker + always_redraw) 등.
- 렌더링: `python scripts/render_anims.py lectures/N강/animations/scenes.py` (빨리 확인하려면 manim `-ql -s`로 마지막 장면만).
- 확인: `python scripts/preview.py frames lectures/N강/animations <scratchpad>/frames` 후 이미지를 Read.

### 4. 비유 사진
- `python scripts/find_images.py search <scratchpad>/img key="english query" ...` → `sheet_*.png`를 Read로 보고 고른다. 영어 검색어가 결과가 좋다. 부족하면 검색어를 바꿔 다시 검색.
- `python scripts/find_images.py fetch <scratchpad>/img lectures/N강/images 이름=key_i ...` → `images/이름.jpg`, `credits.json`, `출처.md`.
- 사람 얼굴이 크게 나온 사진, 상표가 주인공인 사진, 글자가 많은 사진은 피한다.

### 5. 슬라이드 (build_slides.py)
- `Deck(__file__, "N강_<주제>.pptx", footer=("과목", "단원 › 절"))` → `deck.cover(...)`, `deck.ending(...)`, `s = deck.slide(제목, 부제, 부제강조, notes=...)`, 끝에 `deck.credits_slide()`, `deck.save()`.
- 좌표는 EMU. 본문 영역 `L..R`(=838200..11353800), 세로 약 1550000..6200000. 바닥글 6380000.
- `picture(s, "이름", x, y, w, h, focus=(fx, fy))`: 영역에 맞춰 잘림 → 중요한 부분 쪽으로 focus. 사진 아래 출처가 자동으로 붙으니 아래 300000 비워 둔다.
- `video(s, "장면", x, y, w)`: 높이는 w×9/16. 영상 배경색이 슬라이드와 같아 테두리가 없다. 옆 텍스트와 가로로 겹치지 않게 한다.
- 텍스트 마크업: `**굵게**`, `[[강조색]]`, `x_{i}` 아래첨자. 한 슬라이드 본문 글자 크기 15~21pt.
- 실행: `python lectures/N강/build_slides.py` (저장 후 자동 재생까지 설정됨).

### 6. 검수 (반드시)
- `python scripts/preview.py slides lectures/N강/N강_<주제>.pptx <scratchpad>/deck` → `deck_*.png`를 모두 Read.
- 겹침, 잘린 글자, 한 글자만 다음 줄로 넘어간 줄, 영상과 텍스트 충돌, 사진 크롭을 고치고 다시 빌드.
- 영상은 실제 슬라이드쇼 재생까지는 확인 못 하므로, 끝나면 사용자에게 F5로 확인을 부탁한다.

## 주의 (겪었던 문제)
- **LaTeX 없음**: manim에서 `MathTex`, `Tex`, `DecimalNumber`, `Axes.add_coordinates` 쓰지 말 것. 숫자 표시는 `always_redraw(lambda: T(f"{v:.2f}"))`.
- 막대그래프: 범주를 x=1..n에 둔다(`bar_chart`, `x_labels`). x=0에 두면 y축이 첫 막대를 관통한다.
- 글자를 바꿀 때 `Transform` 대신 `FadeTransform`(글자가 뭉개지지 않음). 반복문에서는 바꾼 뒤 `label = new`로 다시 가리켜야 이전 글자가 남지 않는다.
- 템플릿 레이아웃이 쪽 번호 원을 자동으로 그린다 — 직접 그리지 말 것.
- PowerShell 5.1은 BOM 없는 UTF-8 .ps1의 한글 때문에 파싱이 깨진다 → .ps1은 `utf-8-sig`로 저장.
- PowerPoint COM에는 `\` 경로만 넘긴다.
- 웹 요청 헤더(User-Agent 등)에 사용자 이메일 등 개인정보를 넣지 않는다. Flickr(Openverse 경유)는 속도 제한이 심해 Wikimedia Commons를 쓴다.
- manim/렌더링 임시 파일은 scratchpad에 두고, `animations/`에는 `<장면>.mp4`, `<장면>.png`, `scenes.py`만 남긴다.
