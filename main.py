import pygame
import random
import sys
import os

# ─────────────────────────────────────────────
#  아라의 바카라  ·  Millennium Session  v28.0
#  변경사항: MS 팔레트 / 폰트 한글 지원 / 사운드 시스템
# ─────────────────────────────────────────────

pygame.init()
pygame.mixer.init()

info   = pygame.display.Info()
REAL_W = info.current_w if info.current_w > 0 else 360
REAL_H = info.current_h if info.current_h > 0 else 800
SCALE_X = REAL_W / 360
SCALE_Y = REAL_H / 800

screen = pygame.display.set_mode(
    (REAL_W, REAL_H),
    pygame.FULLSCREEN if info.current_w > 0 else 0
)
pygame.display.set_caption("아라의 바카라 — Millennium Session")
clock = pygame.time.Clock()

# ─── [MS 디자인 팔레트 v1.0] ───────────────────
BG       = (15,  15,  35)    # Void        — 배경
DEEP     = (30,  16,  53)    # Deep        — 버튼 기본
GOLD     = (201, 151, 58)    # Antique Gold
GOLD_LT  = (232, 196, 106)   # Gold Light  — 하이라이트
CRIMSON  = (139, 26,  46)    # Crimson     — 취소/위험
CRIMSON_LT=(200, 60,  80)    # Crimson border
EMERALD  = (26,  107, 74)    # Emerald     — Player
GREEN    = (91,  220, 154)   # Green Light
ROYAL    = (61,  43,  106)   # Royal       — PP/TIE
PURPLE   = (184, 158, 232)   # Purple Light
BLUE     = (80,  160, 255)   # Banker accent
GRAY     = (107, 95,  138)   # Muted
WHITE    = (232, 224, 240)   # Soft White
BLACK    = (0,   0,   0)

# ─── [폰트 시스템 — 한글 멀티플랫폼] ───────────
def get_font(size, bold=False):
    scaled = int(size * SCALE_X)
    # 1순위: 로컬 번들 폰트 (프로젝트 폴더에 넣어두면 우선 사용)
    local = ['NanumGothic.ttf', 'malgun.ttf', 'NotoSansKR-Regular.ttf']
    for path in local:
        if os.path.exists(path):
            try: return pygame.font.Font(path, scaled)
            except: pass
    # 2순위: 시스템 경로 탐색 (Android / Linux)
    sys_paths = [
        '/system/fonts/NotoSansCJK-Regular.ttc',
        '/system/fonts/DroidSansFallback.ttf',
        '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/opentype/noto/NotoSansCJKkr-Regular.otf',
    ]
    for path in sys_paths:
        if os.path.exists(path):
            try: return pygame.font.Font(path, scaled)
            except: pass
    # 3순위: SysFont 이름 탐색 (Windows / macOS)
    names = [
        'malgun gothic','malgungothic',
        'Apple SD Gothic Neo','AppleGothic',
        'NanumGothic','NanumBarunGothic',
        'gulim','dotum',
    ]
    for name in names:
        try:
            f = pygame.font.SysFont(name, scaled, bold=bold)
            if f: return f
        except: pass
    # 최후: 시스템 기본 (영문 전용 폴백)
    return pygame.font.Font(None, scaled)

font_ui   = get_font(25)
font_main = get_font(20)
font_card = get_font(45)
font_sym  = get_font(48)
font_sm   = get_font(16)
font_brand= get_font(13)

# ─── [사운드 시스템] ────────────────────────────
# 필요한 파일: sfx_chip.wav / sfx_deal.wav / sfx_win.wav
#              sfx_lose.wav / sfx_levelup.wav / sfx_btn.wav
# 없어도 오류 없이 묵음으로 동작함
def load_sfx(path):
    try:    return pygame.mixer.Sound(path)
    except: return None

sfx = {
    'chip'   : load_sfx('sfx_chip.wav'),
    'deal'   : load_sfx('sfx_deal.wav'),
    'win'    : load_sfx('sfx_win.wav'),
    'lose'   : load_sfx('sfx_lose.wav'),
    'levelup': load_sfx('sfx_levelup.wav'),
    'btn'    : load_sfx('sfx_btn.wav'),
}
def play(name):
    s = sfx.get(name)
    if s: s.play()

# ─── [유틸] ──────────────────────────────────
def sc_x(x): return int(x * SCALE_X)
def sc_y(y): return int(y * SCALE_Y)

def draw_txt(surf, text, font, color, pos):
    surf.blit(font.render(str(text), True, BLACK),  (pos[0]+2, pos[1]+2))
    surf.blit(font.render(str(text), True, color), pos)

def load_img(path, w, h):
    try:
        img = pygame.image.load(path)
        return pygame.transform.smoothscale(img.convert_alpha(), (sc_x(w), sc_y(h)))
    except:
        s = pygame.Surface((sc_x(w), sc_y(h)), pygame.SRCALPHA)
        s.fill((80, 60, 120, 80))
        return s

# ─── [리소스] ────────────────────────────────
VALUES    = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']
SUITS     = [("♥", CRIMSON), ("♦", CRIMSON), ("♣", WHITE), ("♠", WHITE)]
# ※ 특수문자 깨짐 있으면 아래 주석 해제하고 위 줄 주석처리
# SUITS   = [("H", CRIMSON), ("D", CRIMSON), ("C", WHITE), ("S", WHITE)]

card_imgs = [load_img(f'card_{i}.png', 100, 150) for i in range(13)]
card_back = load_img('card_back.png', 100, 150)
table_bg  = load_img('table_bg.png',  340, 400)
cpu_face  = load_img('cpu_face.png',   80, 80)

# ─── [버튼] ──────────────────────────────────
class Button:
    def __init__(self, x, y, w, h, text, bg, border=None, tag=""):
        self.rect   = pygame.Rect(sc_x(x), sc_y(y), sc_x(w), sc_y(h))
        self.text   = text
        self.bg     = bg
        self.border = border or bg
        self.tag    = tag

    def draw(self, surf, badge=0):
        r = self.rect
        pygame.draw.rect(surf, self.bg,     r, border_radius=int(8*SCALE_X))
        pygame.draw.rect(surf, self.border, r, width=1, border_radius=int(8*SCALE_X))
        tw = font_main.size(self.text)[0]
        draw_txt(surf, self.text, font_main, WHITE,
                 (r.centerx - tw//2, r.centery - sc_y(10)))
        if badge > 0:
            br = pygame.Rect(r.x, r.y - sc_y(22), r.w, sc_y(20))
            pygame.draw.rect(surf, GOLD, br, border_radius=int(4*SCALE_X))
            bt = font_sm.render(f"{badge:,}", True, BLACK)
            surf.blit(bt, (r.centerx - bt.get_width()//2, r.y - sc_y(20)))

    def click(self, pos): return self.rect.collidepoint(pos)

# ─── [게임 상태] ─────────────────────────────
level, my_bal, cpu_bal, sel_chip = 1, 100_000, 100_000, 10_000
bets = {"P":0, "B":0, "T":0, "PP":0, "BP":0}
p_cards, b_cards, p_st, b_st = [], [], [], []
game_state = "bet"
show_event = False
event_img  = None
cpu_rect   = pygame.Rect(sc_x(252), sc_y(17), sc_x(80), sc_y(80))
click_cnt  = 0

# ─── [버튼 정의] ─────────────────────────────
chip_btns = [
    Button(15, 460, 60, 35, "1M",  DEEP,    GRAY,        10_000),
    Button(80, 460, 60, 35, "5M",  DEEP,    GRAY,        50_000),
    Button(145,460, 60, 35, "10M", DEEP,    GOLD,        100_000),
    Button(210,460, 60, 35, "ALL", DEEP,    GOLD,        "ALL"),
    Button(275,460, 70, 35, "X",   CRIMSON, CRIMSON_LT,  "CANCEL"),
]
btn_pp   = Button(20, 540,100,45, "PP",     ROYAL,   PURPLE,      "PP")
btn_tie  = Button(130,540,100,45, "TIE",    DEEP,    ROYAL,       "T")
btn_bp   = Button(240,540,100,45, "BP",     DEEP,    BLUE,        "BP")
btn_p    = Button(20, 605,160,75, "PLAYER", EMERALD, GREEN,       "P")
btn_b    = Button(180,605,160,75, "BANKER", DEEP,    BLUE,        "B")
deal_btn = Button(90, 705,180,65, "DEAL!",  GOLD,    GOLD_LT)
next_btn = Button(90, 705,180,65, "NEXT",   CRIMSON, CRIMSON_LT)

# ─── [바카라 점수] ───────────────────────────
def bac_score(cards):
    total = 0
    for v in cards:
        if v == 0:      total += 1   # Ace = 1
        elif v >= 9:    total += 0   # 10,J,Q,K = 0
        else:           total += v + 1
    return total % 10

# ─── [메인 루프] ─────────────────────────────
running = True
while running:
    screen.fill(BG)
    screen.blit(table_bg, (sc_x(10), sc_y(120)))

    # 상단 HUD 패널
    hud = pygame.Surface((sc_x(340), sc_y(108)), pygame.SRCALPHA)
    hud.fill((0, 0, 0, 190))
    screen.blit(hud, (sc_x(10), sc_y(10)))

    # MS 브랜딩 워터마크
    brand = font_brand.render("MILLENNIUM SESSION", True, (65, 48, 95))
    screen.blit(brand, (sc_x(14), sc_y(13)))

    screen.blit(cpu_face, cpu_rect)
    draw_txt(screen, f"CPU: {cpu_bal:,}", font_ui, WHITE,  (sc_x(25), sc_y(27)))
    draw_txt(screen, f"MY : {my_bal:,}",  font_ui, GREEN,  (sc_x(25), sc_y(62)))
    draw_txt(screen, f"Lv.{level}",       font_ui, GOLD,   (sc_x(258), sc_y(108)))

    # ─── 이벤트 처리 ──────────────────────────
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos

            # 치트 (CPU 얼굴 10회 클릭)
            if cpu_rect.collidepoint(pos):
                click_cnt += 1
                if click_cnt >= 10:
                    my_bal += 30_000_000; click_cnt = 0
                continue

            # 레벨업 이벤트 화면 닫기
            if show_event:
                show_event = False; game_state = "bet"; continue

            # ── BET 단계 ──
            if game_state == "bet":
                for cb in chip_btns:
                    if cb.click(pos):
                        play('chip')
                        if cb.tag == "CANCEL":
                            my_bal += sum(bets.values())
                            bets = {k: 0 for k in bets}
                        else:
                            sel_chip = cb.tag

                for area in [btn_p, btn_b, btn_tie, btn_pp, btn_bp]:
                    if area.click(pos):
                        play('btn')
                        amt = my_bal if sel_chip == "ALL" else sel_chip
                        if isinstance(amt, int) and my_bal >= amt:
                            bets[area.tag] += amt; my_bal -= amt

                if deal_btn.click(pos) and sum(bets.values()) > 0:
                    play('deal')
                    p_cards = [random.randint(0,12) for _ in range(2)]
                    b_cards = [random.randint(0,12) for _ in range(2)]
                    p_st    = [random.choice(SUITS) for _ in range(2)]
                    b_st    = [random.choice(SUITS) for _ in range(2)]
                    game_state = "deal1"

            # ── DEAL 단계 ──
            elif game_state in ["deal1","deal2"] and deal_btn.click(pos):
                play('deal')
                game_state = "deal2" if game_state == "deal1" else "deal3"

            # ── 결과 계산 ──
            elif game_state == "deal3" and deal_btn.click(pos):
                ps, bs = bac_score(p_cards), bac_score(b_cards)
                win = 0
                if ps > bs: win += bets["P"] * 2
                if bs > ps: win += int(bets["B"] * 1.95)
                if ps == bs: win += bets["T"] * 8
                if p_cards[0] == p_cards[1]: win += bets["PP"] * 11
                if b_cards[0] == b_cards[1]: win += bets["BP"] * 11
                my_bal  += win
                cpu_bal -= (win - sum(bets.values()))
                play('win' if win > 0 else 'lose')
                if cpu_bal <= 0:
                    level  += 1
                    cpu_bal = 100_000 * level
                    play('levelup')
                    event_img  = load_img(f'ara_level_{min(level-1,12)}.png', 360, 800)
                    show_event = True
                game_state = "result"

            # ── NEXT ──
            elif game_state == "result" and next_btn.click(pos):
                play('btn')
                bets = {k: 0 for k in bets}; game_state = "bet"

    # ─── 렌더링 ───────────────────────────────
    if game_state == "bet":
        chip_lbl = f"{sel_chip:,}" if isinstance(sel_chip, int) else "ALL"
        draw_txt(screen, f"CHIP: {chip_lbl}", font_main, GOLD, (sc_x(135), sc_y(512)))
        for cb in chip_btns: cb.draw(screen)
        btn_pp.draw(screen, bets["PP"])
        btn_tie.draw(screen, bets["T"])
        btn_bp.draw(screen, bets["BP"])
        btn_p.draw(screen, bets["P"])
        btn_b.draw(screen, bets["B"])
        deal_btn.draw(screen)

    elif game_state in ["deal1","deal2","deal3","result"]:
        for side, cards, st, yp in [
            ("P", p_cards, p_st, 190),
            ("B", b_cards, b_st, 390)
        ]:
            if side == "B" and game_state in ["deal1","deal2"]:
                for i in range(2):
                    screen.blit(card_back, (sc_x(60 + i*110), sc_y(yp)))
                continue
            for i, v in enumerate(cards):
                cx, cy = sc_x(60 + i*110), sc_y(yp)
                screen.blit(card_imgs[v], (cx, cy))
                draw_txt(screen, VALUES[v],  font_card, st[i][1], (cx+sc_x(10), cy+sc_y(10)))
                draw_txt(screen, st[i][0],   font_sym,  st[i][1], (cx+sc_x(28), cy+sc_y(62)))

        if game_state == "result":
            ps, bs = bac_score(p_cards), bac_score(b_cards)
            draw_txt(screen, f"P {ps}  :  B {bs}", font_ui, GOLD, (sc_x(118), sc_y(86)))
            next_btn.draw(screen)
        else:
            deal_btn.draw(screen)

    if show_event and event_img:
        screen.blit(event_img, (0, 0))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
