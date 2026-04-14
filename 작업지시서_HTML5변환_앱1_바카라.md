# 작업지시서 — HTML5 게임 변환
**발신: 유리 (Claude · 책임연구원)**
**수신: SOL 대리 (ChatGPT) 또는 재미나이 과장**
**분류: 핵심 변환 작업 / 우선순위 HIGH**

---

## 배경 및 목적

Millennium Session 앱들을 Streamlit + 홈페이지 + 게시판에 배포하기로 결정됨.
Pygame은 서버/브라우저에서 실행 불가 → **HTML5 + 순수 JavaScript** 로 변환 필요.
산출물: **단일 `baccarat.html` 파일** (외부 라이브러리 의존 없음)

---

## 참조 소스

변환 기준 파일: `main.py` (v28.0 · MS 팔레트 적용본)
디자인 기준: Millennium Session Design Identity v1.0

```
MS 팔레트
BG      #0F0F23   (배경)
DEEP    #1E1035   (버튼 기본)
GOLD    #C9973A   (강조)
GOLD_LT #E8C46A   (하이라이트)
CRIMSON #8B1A2E   (취소/위험)
EMERALD #1A6B4A   (Player)
ROYAL   #3D2B6A   (PP/TIE)
BLUE    #50A0FF   (Banker)
WHITE   #E8E0F0   (텍스트)
GRAY    #6B5F8A   (뮤트)
```

---

## 산출물 스펙

### 파일
- **파일명**: `baccarat.html`
- **형태**: 단일 HTML 파일 (CSS · JS 인라인 포함)
- **외부 의존**: 없음 (폰트는 Google Fonts CDN 허용)
- **이미지**: `<img src="card_0.png">` 상대경로 그대로 사용

### 화면 크기
- 기준: **360 × 800px** (모바일 세로)
- Canvas 또는 절대위치 div 레이아웃
- PC에서는 중앙 정렬

### 구현 필수 항목

| 항목 | 내용 |
|------|------|
| 베팅 UI | 칩(1M/5M/10M/ALL/X) + 베팅존(PP/TIE/BP/PLAYER/BANKER) |
| 딜 애니메이션 | 카드 등장 시 슬라이드 또는 페이드인 |
| 점수 계산 | bac_score() 로직 동일하게 JS로 재현 |
| 승패 처리 | 배당률: P×2, B×1.95, T×8, PP×11, BP×11 |
| 레벨업 이벤트 | CPU 파산 시 전체화면 이미지 오버레이 |
| HUD | CPU잔액 / MY잔액 / 레벨 / MS 워터마크 |
| 치트코드 | CPU 얼굴 10회 클릭 → +3천만 |
| 사운드 | Web Audio API 또는 `<audio>` 태그 (sfx_*.wav) |

### 사운드 이벤트
```
sfx_chip.wav    → 칩 클릭
sfx_deal.wav    → 카드 딜
sfx_btn.wav     → 일반 버튼
sfx_win.wav     → 승리
sfx_lose.wav    → 패배
sfx_levelup.wav → 레벨업
```

### 이미지 경로 (상대경로 유지)
```
card_0.png ~ card_12.png   (100×150)
card_back.png               (100×150)
table_bg.png                (340×400)
cpu_face.png                (90×90)
ara_level_1.png ~ 12.png    (360×800)  ← 레벨업 풀스크린
```

---

## 게임 상태 머신

```
bet → (DEAL 클릭) → deal1 → deal2 → deal3 → (DEAL 클릭) → result → (NEXT) → bet
```

---

## 바카라 점수 로직 (JS 변환)

```javascript
// Python bac_score() 를 JS로 변환
function bacScore(cards) {
  let total = 0;
  for (const v of cards) {
    if (v === 0)      total += 1;   // Ace = 1
    else if (v >= 9)  total += 0;   // 10,J,Q,K = 0
    else              total += v + 1;
  }
  return total % 10;
}
```

---

## 품질 기준

- [ ] 모바일 Chrome에서 터치 동작 정상
- [ ] 이미지 없을 때 회색 플레이스홀더 표시 (오류 없음)
- [ ] 사운드 없을 때 묵음 동작 (오류 없음)
- [ ] Streamlit `st.components.v1.html()` 임베드 시 스크롤 없이 표시
- [ ] iframe 임베드 시 정상 동작

---

## 납품

- **파일**: `baccarat.html` 단일 파일
- **위치**: `streamlit_app.py` 와 같은 폴더
- **납품 후**: `streamlit run streamlit_app.py` 로 즉시 확인 가능해야 함

---

**발행일**: 2025  
**담당**: SOL 대리 또는 재미나이 과장 협의 후 결정
