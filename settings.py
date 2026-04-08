# settings.py — All constants, no magic numbers elsewhere

# Window
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
WINDOW_TITLE = "Factory Safety Inspector"
VERSION_LABEL = "v0.1 — Alpha"

# Colors
COLOR_BG = (13, 17, 23)          # #0D1117 dark navy
COLOR_BG_GAME = (13, 40, 24)     # #0D2818 dark green
COLOR_TEXT = (230, 237, 243)     # #E6EDF3 off-white
COLOR_MUTED = (139, 148, 158)    # #8B949E muted gray
COLOR_ACCENT = (240, 192, 64)    # #F0C040 safety yellow
COLOR_BTN_BORDER = (48, 54, 61)  # #30363D default border
COLOR_BTN_HOVER = (240, 192, 64) # #F0C040 hover border

# Font sizes
FONT_SIZE_TITLE = 52
FONT_SIZE_SUBTITLE = 22
FONT_SIZE_BUTTON = 24
FONT_SIZE_BODY = 18
FONT_SIZE_SMALL = 14
FONT_SIZE_TABLE = 17

# Button dimensions
BTN_WIDTH = 280
BTN_HEIGHT = 52
BTN_PADDING = 16
BTN_BORDER_WIDTH = 2

# Layout
TITLE_Y_RATIO = 0.22       # Title vertical position as fraction of screen height
SUBTITLE_OFFSET = 60       # Pixels below title
BUTTON_START_OFFSET = 160  # Pixels below title to first button
BUTTON_GAP = 70            # Vertical gap between buttons

# Factory Select — Card layout
CARD_W = 280
CARD_H = 380
CARD_GAP = 40
CARD_TOP_OFFSET = 20
WORKER_SCALE = 2.0

# Factory Select — SelectButton
SELECT_BTN_W = 180
SELECT_BTN_H = 40
SELECT_BTN_MARGIN = 16

# Factory Select — Difficulty badge colors
COLOR_DIFFICULTY_EASY = (60, 200, 100)
COLOR_DIFFICULTY_MEDIUM = (240, 192, 64)
COLOR_DIFFICULTY_HARD = (220, 60, 60)

# ── Chemical Plant — Layout ────────────────────────────────────────────────────
HUD_HEIGHT = 60                          # px; top strip height

# Factory floor zones (x, y, w, h) — positioned below HUD, above staging
ZONE_REACTOR = (40,   HUD_HEIGHT + 20, 340, 260)
ZONE_STORAGE = (460,  HUD_HEIGHT + 20, 340, 260)
ZONE_MIXING  = (880,  HUD_HEIGHT + 20, 340, 260)

# Staging area — bottom strip
STAGING_AREA_RECT = (0, 580, 1280, 140)

# ── Chemical Plant — Colors ────────────────────────────────────────────────────
COLOR_PLANT_BG         = (28, 32, 36)       # dark charcoal
COLOR_PLANT_GRID       = (40, 46, 52)       # subtle grid lines
COLOR_ZONE_REACTOR     = (80, 30, 30)       # deep red tint
COLOR_ZONE_STORAGE     = (30, 60, 80)       # deep blue tint
COLOR_ZONE_MIXING      = (30, 70, 40)       # deep green tint
COLOR_ZONE_LABEL       = (200, 200, 200)    # zone label text
COLOR_STAGING_BG       = (22, 27, 34)       # staging strip background
COLOR_STAGING_LABEL    = (139, 148, 158)    # muted label

COLOR_SAFETY_BAR       = (60, 200, 100)     # green safety meter fill
COLOR_PRODUCTION_BAR   = (240, 192, 64)     # yellow production meter fill
COLOR_HUD_BG           = (13, 17, 23)       # HUD strip background
COLOR_HUD_TEXT         = (230, 237, 243)    # HUD labels

COLOR_LEAK_CIRCLE      = (255, 160, 0)      # orange leak indicator
COLOR_LEAK_TIMER_BAR   = (255, 80, 0)       # red countdown bar
COLOR_LEAK_TIMER_BG    = (60, 60, 60)       # countdown bar background

COLOR_WORKER_SELECTED  = (240, 192, 64)     # highlight ring around selected worker
COLOR_ASSIGN_BTN       = (60, 200, 100)     # "Assign Respirator" button fill
COLOR_ASSIGN_BTN_TEXT  = (13, 17, 23)       # button label

COLOR_EXPLOSION_INNER  = (255, 160, 0)      # orange inner ring
COLOR_EXPLOSION_OUTER  = (220, 40, 40)      # red outer ring
COLOR_EXPLOSION_TEXT   = (255, 255, 255)    # "EXPLOSION!" text

COLOR_GAME_OVER_BG     = (13, 17, 23)       # game-over overlay background
COLOR_GRADE_A          = (60, 200, 100)
COLOR_GRADE_B          = (240, 192, 64)
COLOR_GRADE_C          = (240, 140, 40)
COLOR_GRADE_F          = (220, 60, 60)

COLOR_LEVEL_UP_TEXT    = (240, 192, 64)     # "LEVEL UP!" notification

# ── Chemical Plant — Leak mechanic ────────────────────────────────────────────
LEAK_HIT_RADIUS        = 24              # px; click detection radius
LEAK_CIRCLE_RADIUS     = 18             # px; drawn circle radius
LEAK_TIMER_BAR_W       = 48             # px; width of countdown bar
LEAK_TIMER_BAR_H       = 6              # px; height of countdown bar
LEAK_TIMER_EASY        = 8.0            # seconds (Level 1)
LEAK_TIMER_MEDIUM      = 5.0            # seconds (Level 2)
LEAK_TIMER_HARD        = 3.0            # seconds (Level 3)
LEAK_MAX_SIMULTANEOUS  = 3              # absolute max (Level 3 value; used as list cap)

# ── Chemical Plant — Worker mechanic ──────────────────────────────────────────
WORKER_INTERVAL_EASY   = 15.0           # seconds between spawns (Level 1)
WORKER_INTERVAL_MEDIUM = 10.0           # seconds between spawns (Level 2)
WORKER_INTERVAL_HARD   = 6.0            # seconds between spawns (Level 3)
WORKER_SPACING         = 80             # px; horizontal gap between workers in staging
WORKER_STAGING_Y       = 650            # px; vertical centre of workers in staging
ASSIGN_BTN_W           = 200            # px
ASSIGN_BTN_H           = 36             # px
ASSIGN_BTN_X           = 1060           # px; left edge of button
ASSIGN_BTN_Y           = 670            # px; top edge of button

# ── Chemical Plant — Scoring ───────────────────────────────────────────────────
SCORE_LEAK_RESOLVED         = 100
SCORE_WORKER_PROTECTED      = 50
SAFETY_PENALTY_UNPROTECTED_WORKER = 10.0   # percentage points

# ── Chemical Plant — Difficulty / progression ─────────────────────────────────
LEVEL_ADVANCE_DURATION      = 60.0      # seconds per level
LEVEL_UP_DISPLAY_DURATION   = 2.0       # seconds "LEVEL UP!" is shown
PRODUCTION_RATE             = 5.0       # % per second

# ── Chemical Plant — Explosion animation ──────────────────────────────────────
EXPLOSION_FRAME_DURATION    = 133       # ms per frame  (400 / 3 ≈ 133)
EXPLOSION_TOTAL_DURATION    = 400       # ms total
EXPLOSION_TEXT_HOLD_DURATION = 1.0     # seconds pause after animation before game-over

# ── Chemical Plant — HUD bar geometry ─────────────────────────────────────────
HUD_BAR_W        = 200    # px; max width of each meter bar
HUD_BAR_H        = 16     # px; height of each meter bar
HUD_BAR_MARGIN   = 8      # px; gap between bar bg and fill
