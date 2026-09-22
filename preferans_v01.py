import math
import random
import threading
import pygame

# ------------------------------------------------------------
# Преферанс — версия 0.629
# Главный экран + первая раздача на 3 игроков
# ------------------------------------------------------------

pygame.init()

WIDTH, HEIGHT = 1600, 900
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Преферанс")

clock = pygame.time.Clock()

font = pygame.font.SysFont("Georgia", 34, bold=True)
button_font = pygame.font.SysFont("Georgia", 44, bold=True)
title_font = pygame.font.SysFont("Georgia", 48, bold=True)

# ------------------------------------------------------------
# Цвета
# ------------------------------------------------------------

BACKGROUND = (24, 23, 22)
WOOD_DARK = (38, 27, 22)
WOOD_LIGHT = (76, 54, 39)
METAL = (74, 78, 78)

GOLD = (180, 148, 83)
GOLD_DARK = (105, 78, 42)
GOLD_LIGHT = (218, 185, 112)

IVORY = (239, 229, 199)

RED = (190, 35, 30)
RED_LIGHT = (245, 65, 55)

BLACK = (24, 23, 20)

FLAME = (255, 190, 65)

GREEN = (55, 145, 65)
GREEN_LIGHT = (75, 190, 85)

BID_BUTTON = (185, 164, 64)
BID_BUTTON_HOVER = (162, 242, 153)

BID_TEXT_FONT = pygame.font.SysFont(
    "Georgia",
    38,
    bold=True
)

BID_SUIT_FONT = pygame.font.SysFont(
    "DejaVu Sans",
    54,
    bold=True
)

# ------------------------------------------------------------
# Размеры кнопок
# ------------------------------------------------------------

BUTTON_WIDTH = 300
BUTTON_HEIGHT = 75

# ------------------------------------------------------------
# Размеры игровых карт
# ------------------------------------------------------------

CARD_W = 120
CARD_H = 175

# ------------------------------------------------------------
# Состояние игры
# ------------------------------------------------------------

game_started = False

player_hands = [[], [], []]

# Две карты прикупа
talon = []

# ============================================================
# СОСТОЯНИЕ ТОРГОВЛИ
# ============================================================

# 0 — мы, 1 — левый бот, 2 — правый бот
dealer = 0
current_bidder = 0

bidding_active = False
bidding_finished = False

# Возможные заявки
BID_OPTIONS = [
    "6♠",
    "6♣",
    "6♦",
    "6♥",
    "6БК",

    "7♠",
    "7♣",
    "7♦",
    "7♥",
    "7БК",

    "8♠",
    "8♣",
    "8♦",
    "8♥",
    "8БК",

    "9♠",
    "9♣",
    "9♦",
    "9♥",
    "9БК",

    "10♠",
    "10♣",
    "10♦",
    "10♥",
    "10БК",

    "Мизер",
    "Пас"
]

player_bids = ["", "", ""]
player_passed = [False, False, False]

# История всех заявок в текущей торговле
bid_history = []

# Текущая заявка
highest_bid = ""

# Текст над картами соперников
opponent_actions = ["", ""]

# Количество взяток у игроков
tricks_won = [0, 0, 0]

# ============================================================
# СОСТОЯНИЕ ПОСЛЕ ТОРГОВЛИ
# ============================================================

game_phase = "bidding"
declarer = None
declarer_contract = ""

discard_selection = []
discard_button_rect = None
whist_button_rects = []
whist_choice = None

talon_taken = False

# ============================================================
# СОСТОЯНИЕ ВИСТА
# ============================================================

whist_current_player = None
whist_actions = ["", ""]
play_current_player = None
trick_cards = []
trick_lead_suit = None
trick_winner = None
trick_number = 0
played_cards = []

# Прямоугольники кнопок торговли
bid_buttons = []

# ============================================================
# СОСТОЯНИЕ РАЗМЫШЛЕНИЯ ИИ
# ============================================================

bot_thinking = False
bot_result = None
bot_result_player = None

def start_bidding():

    global dealer
    global current_bidder
    global bidding_active
    global bidding_finished
    global player_bids
    global highest_bid
    global opponent_actions
    global tricks_won
    global player_passed
    global bid_history
    global game_phase
    global declarer
    global declarer_contract
    global talon_taken

    dealer = random.randint(0, 2)

    # Первым торгует игрок слева от раздающего
    current_bidder = (dealer + 1) % 3

    bidding_active = True
    bidding_finished = False

    player_bids = ["", "", ""]
    player_passed = [False, False, False]
    highest_bid = ""
    bid_history = []

    opponent_actions = ["", ""]

    discard_selection.clear()

    game_phase = "bidding"
    declarer = None
    declarer_contract = ""
    talon_taken = False


# ============================================================
# КОЛОДА
# ============================================================

def create_deck():

    suits = ["♠", "♥", "♦", "♣"]
    ranks = ["7", "8", "9", "10", "В", "Д", "К", "Т"]

    return [
        (rank, suit)
        for suit in suits
        for rank in ranks
    ]


# ============================================================
# РАЗДАЧА
# ============================================================

def deal_cards():

    global player_hands, talon

    deck = create_deck()
    random.shuffle(deck)

    player_hands = [[], [], []]
    talon = []

    # --------------------------------------------------------
    # Первый круг — по 2 карты каждому
    # --------------------------------------------------------

    for _ in range(2):

        for player in range(3):

            player_hands[player].append(
                deck.pop()
            )

    # --------------------------------------------------------
    # Прикуп — 2 карты
    # --------------------------------------------------------

    talon.append(deck.pop())
    talon.append(deck.pop())

    # --------------------------------------------------------
    # Второй круг — по 3 карты каждому
    # --------------------------------------------------------

    for _ in range(3):

        for player in range(3):

            player_hands[player].append(
                deck.pop()
            )

    # --------------------------------------------------------
    # Третий круг — ещё по 3 карты каждому
    # --------------------------------------------------------

    for _ in range(3):

        for player in range(3):

            player_hands[player].append(
                deck.pop()
            )

    # --------------------------------------------------------
    # Четвёртый круг — ещё по 2 карты каждому
    # --------------------------------------------------------

    for _ in range(2):

        for player in range(3):

            player_hands[player].append(
                deck.pop()
            )

    # --------------------------------------------------------
    # Сортировка нашей руки
    #
    # Старшинство мастей в преферансе:
    #
    # ♠ пики
    # ♣ трефы
    # ♦ бубны
    # ♥ червы
    #
    # Внутри масти:
    #
    # 7 8 9 10 В Д К Т
    # --------------------------------------------------------

    suit_order = {
        "♠": 0,
        "♣": 1,
        "♦": 2,
        "♥": 3
    }

    rank_order = {
        "7": 0,
        "8": 1,
        "9": 2,
        "10": 3,
        "В": 4,
        "Д": 5,
        "К": 6,
        "Т": 7
    }

    player_hands[0].sort(
        key=lambda card: (
            suit_order[card[1]],
            rank_order[card[0]]
        )
    )


# ============================================================
# СТОЛ
# ============================================================

def draw_wood_table(surface):

    surface.fill(BACKGROUND)

    table_rect = pygame.Rect(
        55,
        45,
        WIDTH - 110,
        HEIGHT - 90
    )

    pygame.draw.rect(
        surface,
        WOOD_DARK,
        table_rect,
        border_radius=24
    )

    pygame.draw.rect(
        surface,
        METAL,
        table_rect,
        width=3,
        border_radius=24
    )

    pygame.draw.rect(
        surface,
        (112, 82, 54),
        table_rect.inflate(-12, -12),
        width=2,
        border_radius=18
    )

    wood_random = random.Random(7)

    for _ in range(65):

        y = wood_random.randint(
            70,
            HEIGHT - 70
        )

        x = wood_random.randint(
            70,
            WIDTH - 180
        )

        length = wood_random.randint(
            50,
            230
        )

        points = []

        for step in range(9):

            px = x + step * length / 8

            py = y + math.sin(
                step * 0.8
            ) * wood_random.randint(1, 5)

            points.append(
                (px, py)
            )

        pygame.draw.lines(
            surface,
            WOOD_LIGHT,
            False,
            points,
            1
        )

    inner = pygame.Rect(
        170,
        130,
        WIDTH - 340,
        HEIGHT - 260
    )

    pygame.draw.rect(
        surface,
        (43, 49, 46),
        inner,
        border_radius=30
    )

    pygame.draw.rect(
        surface,
        (113, 99, 67),
        inner,
        width=2,
        border_radius=30
    )

    pygame.draw.rect(
        surface,
        (72, 78, 70),
        inner.inflate(-18, -18),
        width=1,
        border_radius=24
    )


# ============================================================
# ПОДСВЕЧНИКИ
# ============================================================

def draw_candelabra(surface, x, y, scale=1.0):

    metal = (105, 91, 68)
    dark_metal = (48, 43, 35)

    def s(value):
        return int(value * scale)

    base = pygame.Rect(
        x - s(42),
        y + s(42),
        s(84),
        s(14)
    )

    pygame.draw.ellipse(
        surface,
        dark_metal,
        base
    )

    pygame.draw.ellipse(
        surface,
        metal,
        base,
        width=max(1, s(2))
    )

    pygame.draw.rect(
        surface,
        metal,
        pygame.Rect(
            x - s(5),
            y - s(20),
            s(10),
            s(65)
        )
    )

    pygame.draw.circle(
        surface,
        metal,
        (x, y + s(12)),
        s(9)
    )

    for direction in (-1, 0, 1):

        bx = x + direction * s(30)

        by = y - (
            s(2)
            if direction
            else s(16)
        )

        pygame.draw.line(
            surface,
            metal,
            (x, y + s(5)),
            (bx, by),
            max(1, s(4))
        )

        pygame.draw.rect(
            surface,
            metal,
            pygame.Rect(
                bx - s(5),
                by - s(22),
                s(10),
                s(24)
            )
        )

        flame_center = (
            bx,
            by - s(31)
        )

        pygame.draw.ellipse(
            surface,
            (191, 111, 32),
            pygame.Rect(
                flame_center[0] - s(8),
                flame_center[1] - s(14),
                s(16),
                s(28)
            )
        )

        pygame.draw.ellipse(
            surface,
            FLAME,
            pygame.Rect(
                flame_center[0] - s(4),
                flame_center[1] - s(10),
                s(8),
                s(19)
            )
        )

    glow = pygame.Surface(
        (s(150), s(150)),
        pygame.SRCALPHA
    )

    pygame.draw.circle(
        glow,
        (255, 170, 55, 18),
        (s(75), s(75)),
        s(60)
    )

    surface.blit(
        glow,
        (x - s(75), y - s(75))
    )


# ============================================================
# ЛИЦЕВАЯ СТОРОНА КАРТЫ
# ============================================================

def draw_card_face(
    surface,
    rect,
    rank="Т",
    suit="♠"
):

    pygame.draw.rect(
        surface,
        IVORY,
        rect,
        border_radius=7
    )

    pygame.draw.rect(
        surface,
        (102, 75, 45),
        rect,
        width=2,
        border_radius=7
    )

    color = (
        RED
        if suit in ("♥", "♦")
        else BLACK
    )

    rank_size = max(62, rect.width // 3)

    if rank == "К":
    	rank_size = 58

    if rank == "Т":
    	rank_size = 70

    if rank == "7":
    	rank_size = 66

    if rank == "8":
    	rank_size = 65

    if rank == "9":
    	rank_size = 65

    if rank == "10":
    	rank_size = 68

    rank_font = pygame.font.SysFont(
        "Georgia",
        rank_size,
        bold=True
    )

    suit_font = pygame.font.SysFont(
        "DejaVu Sans",
        max(86, rect.width // 3)
    )

    rank_image = rank_font.render(
        rank,
        True,
        color
    )

    suit_image = suit_font.render(
        suit,
        True,
        color
    )

    rank_x = rect.left + 7
    rank_y = rect.top + 5

    if rank == "7":
        rank_x = rect.left + 16
        rank_y = rect.top + 4

    if rank == "8":
        rank_x = rect.left + 10
        rank_y = rect.top + 14

    if rank == "9":
        rank_x = rect.left + 11
        rank_y = rect.top + 1

    if rank == "К":
        rank_x = rect.left + 6

    if rank == "Т":
        rank_x = rect.left + 36    

    surface.blit(
        rank_image,
        (
            rank_x,
            rank_y
        )
    )

    # --------------------------------------------------------
    # Дама — цветок
    # --------------------------------------------------------

    if rank == "Д":

        flower_color = color

        fx = rect.left + 88
        fy = rect.top + 29

        # Стебель
        pygame.draw.lines(
            surface,
            flower_color,
            False,
            [
                (fx,      fy + 2),
                (fx - 2,  fy + 13),
                (fx - 3,  fy + 25),
                (fx - 1,  fy + 36),
                (fx + 2,  fy + 46),
            ],
            3
        )

        # Левый листик
        pygame.draw.ellipse(
            surface,
            flower_color,
            pygame.Rect(
                fx - 22,
                fy + 25,
                23,
                10
            ),
            width=2
        )

        # Правый листик
        pygame.draw.ellipse(
            surface,
            flower_color,
            pygame.Rect(
                fx - 1,
                fy + 31,
                23,
                10
            ),
            width=2
        )

        # Лепестки
        petal_data = [
            (0, -15, 0),
            (-13, -8, 45),
            (-13, 8, 135),
            (13, -8, -45),
            (13, 8, -135),
        ]

        for px, py, angle in petal_data:

            petal_surface = pygame.Surface(
                (22, 22),
                pygame.SRCALPHA
            )

            pygame.draw.ellipse(
                petal_surface,
                flower_color,
                pygame.Rect(
                    3,
                    2,
                    17,
                    18
                ),
                width=4
            )

            rotated = pygame.transform.rotate(
                petal_surface,
                angle
            )

            petal_rect = rotated.get_rect(
                center=(
                    fx + px,
                    fy + py
                )
            )

            surface.blit(
                rotated,
                petal_rect
            )

        # Сердцевина
        pygame.draw.circle(
            surface,
            flower_color,
            (fx, fy - 1),
            4
        )

        pygame.draw.circle(
            surface,
            IVORY,
            (fx, fy - 1),
            1
        )

    # --------------------------------------------------------
    # Король — корона
    # --------------------------------------------------------

    if rank == "К":

        cx = rect.left + 88.5
        cy = rect.top + 42

        crown_color = color

        crown = [
            (cx - 24, cy + 16),
            (cx - 18, cy - 11),
            (cx - 9,  cy + 1),
            (cx,      cy - 19),
            (cx + 9,  cy + 1),
            (cx + 18, cy - 11),
            (cx + 24, cy + 16),
        ]

        pygame.draw.polygon(
            surface,
            crown_color,
            crown
        )

        pygame.draw.line(
            surface,
            IVORY,
            (cx - 19, cy - 10),
            (cx - 14, cy + 9),
            2
        )

        pygame.draw.line(
            surface,
            IVORY,
            (cx, cy - 18),
            (cx, cy + 9),
            2
        )

        pygame.draw.line(
            surface,
            IVORY,
            (cx + 19, cy - 10),
            (cx + 14, cy + 9),
            2
        )

        for dx, dy in (
            (-20, -16),
            (0, -27.5),
            (20.5, -17)
        ):

            pygame.draw.circle(
                surface,
                crown_color,
                (cx + dx, cy + dy),
                7
            )

        pygame.draw.rect(
            surface,
            crown_color,
            pygame.Rect(
                cx - 23,
                cy + 8,
                47,
                10.5
            )
        )

        pygame.draw.line(
            surface,
            IVORY,
            (cx - 20, cy + 13),
            (cx + 20, cy + 13),
            2
        )

        for dx in (-10, 0, 10):

            pygame.draw.circle(
                surface,
                IVORY,
                (cx + dx, cy + 14),
                2.5
            )

    # --------------------------------------------------------
    # Валет — алебарда
    # --------------------------------------------------------

    if rank == "В":

        axe_color = color

        x_bottom = rect.left + 64
        y_bottom = rect.top + 68

        x_top = rect.left + 88
        y_top = rect.top + 19

        pygame.draw.line(
            surface,
            axe_color,
            (x_bottom, y_bottom),
            (x_top, y_top),
            4
        )

        blade = [
            (x_top - 4,  y_top + 5),
            (x_top + 14, y_top - 1),
            (x_top + 23, y_top + 4),
            (x_top + 15, y_top + 37),
            (x_top + 5,  y_top + 44),
            (x_top - 2,  y_top + 37),
            (x_top + 5,  y_top + 9),
            (x_top - 4,  y_top + 13),
        ]

        pygame.draw.polygon(
            surface,
            axe_color,
            blade
        )

        pygame.draw.polygon(
            surface,
            axe_color,
            [
                (x_top - 3, y_top + 7),
                (x_top + 6, y_top + 4),
                (x_top + 3, y_top + 16),
                (x_top - 2, y_top + 18),
            ]
        )

        pygame.draw.line(
            surface,
            IVORY,
            (x_top + 9, y_top + 9),
            (x_top + 4, y_top + 34),
            3
        )

        pygame.draw.polygon(
            surface,
            axe_color,
            [
                (x_top - 4, y_top + 5),
                (x_top + 2, y_top - 9),
                (x_top + 8, y_top + 2),
            ]
        )

        pygame.draw.polygon(
            surface,
            axe_color,
            [
                (x_bottom - 3, y_bottom - 3),
                (x_bottom + 1, y_bottom + 7),
                (x_bottom + 5, y_bottom - 4),
            ]
        )

    # --------------------------------------------------------
    # Масть
    # --------------------------------------------------------

    surface.blit(
        suit_image,
        suit_image.get_rect(
            center=rect.center
        ).move(0, 18)
    )


# ============================================================
# РУБАШКА КАРТЫ
# ============================================================

def draw_card_back(surface, rect):

    pygame.draw.rect(
        surface,
        (48, 55, 62),
        rect,
        border_radius=7
    )

    pygame.draw.rect(
        surface,
        GOLD,
        rect,
        width=2,
        border_radius=7
    )

    inner = rect.inflate(
        -9,
        -9
    )

    pygame.draw.rect(
        surface,
        (70, 78, 83),
        inner,
        width=1,
        border_radius=4
    )

    cx, cy = rect.center

    pygame.draw.polygon(
        surface,
        GOLD_DARK,
        [
            (cx, rect.top + 18),
            (rect.right - 17, cy),
            (cx, rect.bottom - 18),
            (rect.left + 17, cy),
        ],
        width=2
    )

    pygame.draw.circle(
        surface,
        GOLD,
        (cx, cy),
        4
    )


# ============================================================
# ИМЕНА ИГРОКОВ
# ============================================================

def draw_players(surface):

    positions = [
        (WIDTH // 2 - 55, HEIGHT - 28),
        (95, HEIGHT // 2),
        (WIDTH - 95, HEIGHT // 2),
    ]

    names = [
        "ВЫ —",
        "СТУДЕНТ",
        "ДОЦЕНТ"
    ]

    tricks_font = pygame.font.SysFont(
        "Georgia",
        34,
        bold=True
    )

    for index, (x, y) in enumerate(positions):

        name = names[index]

        label = font.render(
            name,
            True,
            IVORY
        )

        label_rect = label.get_rect(
            center=(x, y)
        )

        surface.blit(
            label,
            label_rect
        )

        # ----------------------------------------------------
        # Количество взяток
        # ----------------------------------------------------

        tricks_text = f"ВЗЯЛ: {tricks_won[index]}"

        tricks_label = tricks_font.render(
            tricks_text,
            True,
            IVORY
        )

        if index == 0:

            tricks_rect = tricks_label.get_rect(
                midleft=(
                    label_rect.right + 18,
                    y
                )
            )

        else:

            tricks_rect = tricks_label.get_rect(
                center=(
                    x,
                    y + 48
                )
            )

        surface.blit(
            tricks_label,
            tricks_rect
        )


# ============================================================
# ДЕМОНСТРАЦИОННЫЕ КАРТЫ ГЛАВНОГО МЕНЮ
# ============================================================

def draw_demo_cards(surface):

    card_w = 120
    card_h = 175

    start_x = WIDTH // 2 - (
        card_w * 2 + 18 * 1.5
    )

    y = HEIGHT // 2 - card_h // 2

    demo = [
        ("Т", "♠"),
        ("Д", "♥"),
        ("К", "♣"),
        ("В", "♦"),
    ]

    for i, (rank, suit) in enumerate(demo):

        rect = pygame.Rect(
            start_x + i * (card_w + 18),
            y,
            card_w,
            card_h
        )

        draw_card_face(
            surface,
            rect,
            rank,
            suit
        )

# ============================================================
# НАША ЗАЯВКА
# ============================================================

def draw_player_action(surface):

    if not player_bids[0]:
        return

    text = (
        declarer_contract
        if game_phase in ("whist", "whist_done")
        else player_bids[0]
    )

    if game_phase == "play":

        action_font = pygame.font.SysFont(
            "Georgia",
            40,
            bold=True
        )

        suit_font = pygame.font.SysFont(
            "DejaVu Sans",
            52,
            bold=True
        )

    else:

        action_font = pygame.font.SysFont(
            "Georgia",
            64
        )

        suit_font = pygame.font.SysFont(
            "DejaVu Sans",
            86
        )

    suit_colors = {
        "♠": BLACK,
        "♣": BLACK,
        "♦": RED,
        "♥": RED
    }

    parts = []

    for char in text:

        if char in suit_colors:

            image = suit_font.render(
                char,
                True,
                suit_colors[char]
            )

        else:

            image = action_font.render(
                char,
                True,
                BLACK
            )

        parts.append(image)

    total_width = sum(
        image.get_width()
        for image in parts
    )

    if game_phase == "play":

        x = WIDTH // 2 - total_width // 2
        y = HEIGHT - CARD_H - 115

        padding_x = 10
        padding_y = 4

    else:

        x = WIDTH // 2 - total_width // 2
        y = HEIGHT - CARD_H - 165

        padding_x = 20
        padding_y = 8

    background_rect = pygame.Rect(
        x - padding_x,
        y - padding_y,
        total_width + padding_x * 2,
        55 if game_phase == "play" else 100
    )

    pygame.draw.rect(
        surface,
        IVORY,
        background_rect,
        border_radius=10
    )

    pygame.draw.rect(
        surface,
        GOLD,
        background_rect,
        width=2,
        border_radius=10
    )

    for image in parts:

        image_rect = image.get_rect(
            midleft=(
                x,
                y + 42
            )
        )

        surface.blit(
            image,
            image_rect
        )

        x += image.get_width()

def draw_opponent_actions(surface):

    whist_display_actions = {}

    if (
        game_phase in ("whist", "whist_done")
        and declarer is not None
    ):

        whist_display_actions = {
            (declarer + 1) % 3: whist_actions[0],
            (declarer + 2) % 3: whist_actions[1]
        }

    # Шрифт для обычного текста
    font = pygame.font.SysFont(
        "Georgia",
        64
    )

    # Шрифт, который умеет рисовать ♠ ♣ ♦ ♥
    suit_font = pygame.font.SysFont(
        "DejaVu Sans",
        86
    )

    # ----------------------------------------------------
    # Левый соперник
    # ----------------------------------------------------

    if (
        opponent_actions[0]
        or (
            1 in whist_display_actions
            and whist_display_actions[1] != ""
        )
    ):

        text = (
            whist_display_actions[1]
            if game_phase in ("whist", "whist_done")
            and whist_display_actions[1] != ""
            else opponent_actions[0]
        )

        x = 190
        y = 250

        background_rect = pygame.Rect(
            x - 12,
            y - 8,
            215,
            100
        )

        pygame.draw.rect(
            surface,
            IVORY,
            background_rect,
            border_radius=10
        )

        pygame.draw.rect(
            surface,
            GOLD,
            background_rect,
            width=2,
            border_radius=10
        )

        # Рисуем строку посимвольно,
        # чтобы масть гарантированно была DejaVu Sans

        current_x = x

        for char in text:

            if char in "♠♣♦♥":

                suit_color = (
                    RED
                    if char in "♦♥"
                    else BLACK
                )

                char_surface = suit_font.render(
                    char,
                    True,
                    suit_color
                )

            else:

                char_surface = font.render(
                    char,
                    True,
                    BLACK
                )

            surface.blit(
                char_surface,
                (current_x, y)
            )

            current_x += char_surface.get_width()

    # ----------------------------------------------------
    # Правый соперник
    # ----------------------------------------------------

    if (
        opponent_actions[1]
        or (
            2 in whist_display_actions
            and whist_display_actions[2] != ""
        )
    ):

        text = (
            whist_display_actions[2]
            if (
                2 in whist_display_actions
                and whist_display_actions[2] != ""
            )
            else opponent_actions[1]
        )

        x = WIDTH - 275
        y = 250

        background_rect = pygame.Rect(
            x - 12,
            y - 8,
            215,
            100
        )

        pygame.draw.rect(
            surface,
            IVORY,
            background_rect,
            border_radius=10
        )

        pygame.draw.rect(
            surface,
            GOLD,
            background_rect,
            width=2,
            border_radius=10
        )        

        current_x = x

        for char in text:

            if char in "♠♣♦♥":

                suit_color = (
                    RED
                    if char in "♦♥"
                    else BLACK
                )

                char_surface = suit_font.render(
                    char,
                    True,
                    suit_color
                )

            else:

                char_surface = font.render(
                    char,
                    True,
                    BLACK
                )

            surface.blit(
                char_surface,
                (current_x, y)
            )

            current_x += char_surface.get_width()


# ============================================================
# КАРТЫ ВО ВРЕМЯ ИГРЫ
# ============================================================

def draw_game_cards(surface):

    # --------------------------------------------------------
    # Наши 10 карт — снизу
    #
    # Внутри одной масти карты идут вплотную.
    # Между мастями есть небольшой промежуток.
    # --------------------------------------------------------

    hand = player_hands[0]

    same_suit_step = CARD_W
    new_suit_gap = 18

    # --------------------------------------------------------
    # Рассчитываем общую ширину руки
    # --------------------------------------------------------

    total_width = 0

    for index, card in enumerate(hand):

        total_width += same_suit_step

        if (
            index > 0
            and card[1] != hand[index - 1][1]
        ):

            total_width += new_suit_gap

    total_width -= same_suit_step

    start_x = (
        WIDTH // 2
        - total_width // 2
        - 60
    )

    y = HEIGHT - CARD_H - 55

    current_x = start_x

    for index, (rank, suit) in enumerate(hand):

        # ----------------------------------------------------
        # Новая масть — небольшой разделительный промежуток
        # ----------------------------------------------------

        if (
            index > 0
            and suit != hand[index - 1][1]
        ):

            current_x += new_suit_gap

        selected = index in discard_selection

        card_y = y

        if selected:
            card_y -= 20

        rect = pygame.Rect(
            current_x,
            card_y,
            CARD_W,
            CARD_H
        )

        draw_card_face(
            surface,
            rect,
            rank,
            suit
        )

        # ----------------------------------------------------
        # Салатовая полупрозрачная подсветка выбранной карты
        # ----------------------------------------------------

        if selected:

            highlight = pygame.Surface(
                (CARD_W, CARD_H),
                pygame.SRCALPHA
            )

            highlight.fill(
                (19, 235, 48, 5)
            )

            surface.blit(
                highlight,
                rect
            )

            pygame.draw.rect(
                surface,
                GREEN,
                rect,
                width=4,
                border_radius=8
            )

        current_x += same_suit_step

    # --------------------------------------------------------
    # Бот слева — закрытые карты
    # --------------------------------------------------------

    left_x = 185
    left_y = HEIGHT // 2 - 90

    for index in range(10):

        rect = pygame.Rect(
            left_x + index * 3,
            left_y + index * 3,
            CARD_W,
            CARD_H
        )

        draw_card_back(
            surface,
            rect
        )

    # --------------------------------------------------------
    # Бот справа — закрытые карты
    # --------------------------------------------------------

    right_x = WIDTH - 261
    right_y = HEIGHT // 2 - 90

    for index in range(10):

        rect = pygame.Rect(
            right_x - index * 3,
            right_y + index * 3,
            CARD_W,
            CARD_H
        )

        draw_card_back(
            surface,
            rect
        )

    # --------------------------------------------------------
    # Прикуп — две закрытые карты справа от надписи
    # --------------------------------------------------------

    if game_phase == "bidding":

        talon_x = WIDTH // 2 + 80
        talon_y = 30

        talon_label = font.render(
            "ПРИКУП",
            True,
            GOLD_LIGHT
        )

        surface.blit(
            talon_label,
            talon_label.get_rect(
                midright=(
                    talon_x - 15,
                    talon_y + 65
                )
            )
        )

        for index in range(2):

            rect = pygame.Rect(
                talon_x + index * 16,
                talon_y - 10,
                CARD_W,
                CARD_H
            )

            draw_card_back(
                surface,
                rect
            )

def draw_discard_button(surface, mouse_pos):

    global discard_button_rect

    discard_button_rect = None

    if game_phase != "discard":
        return

    if len(discard_selection) != 2:
        return

    button_width = 340
    button_height = 95

    discard_button_rect = pygame.Rect(
        WIDTH // 2 - button_width // 2,
        HEIGHT - 450,
        button_width,
        button_height
    )

    hovered = discard_button_rect.collidepoint(
        mouse_pos
    )

    if hovered:

        pygame.draw.rect(
            surface,
            (125, 9, 9),
            discard_button_rect,
            border_radius=10
        )

    else:

        pygame.draw.rect(
            surface,
            BLACK,
            discard_button_rect,
            border_radius=10
        )

    pygame.draw.rect(
        surface,
        GOLD,
        discard_button_rect,
        width=2,
        border_radius=10
    )

    discard_font = pygame.font.SysFont("Georgia", 67, bold=True)

    text = discard_font.render(
        "СНЕСТИ",
        True,
        GOLD
    )

    surface.blit(
        text,
        text.get_rect(
            center=discard_button_rect.center
        )
    )

# ============================================================
# СОСТОЯНИЕ ПОСЛЕ СНОСА
# ============================================================

def draw_discard_done(surface):

    if game_phase != "discard_done":
        return

    title_font = pygame.font.SysFont(
        "Georgia",
        64,
        bold=True
    )

    text_font = pygame.font.SysFont(
        "Georgia",
        34,
        bold=True
    )

    title = title_font.render(
        "СНОС ЗАВЕРШЁН",
        True,
        GOLD
    )

    surface.blit(
        title,
        title.get_rect(
            center=(
                WIDTH // 2,
                220
            )
        )
    )

    text = text_font.render(
        "Ожидание вистующих...",
        True,
        IVORY
    )

    surface.blit(
        text,
        text.get_rect(
            center=(
                WIDTH // 2,
                290
            )
        )
    )

# ============================================================
# ВИСТ
# ============================================================

def draw_whist_phase(surface, mouse_pos):

    global whist_button_rects

    whist_button_rects = []

    if (
        game_phase != "whist"
        or whist_current_player != 0
    ):
        return

    title_font = pygame.font.SysFont(
        "Georgia",
        94,
        bold=True
    )

    button_font = pygame.font.SysFont(
        "Georgia",
        42,
        bold=True
    )

    title = title_font.render(
        "ВИСТ",
        True,
        GOLD
    )

    surface.blit(
        title,
        title.get_rect(
            center=(
                WIDTH // 2,
                210
            )
        )
    )

    button_width = 280
    button_height = 95
    gap = 25

    total_width = (
        button_width * 3
        + gap * 2
    )

    start_x = (
        WIDTH // 2
        - total_width // 2
    )

    y = 360

    buttons = [
        ("ВИСТ", GREEN),
        ("ПОЛВИСТА", GOLD_LIGHT),
        ("ПАС", RED)
    ]

    for index, (text, color) in enumerate(buttons):

        rect = pygame.Rect(
            start_x
            + index * (button_width + gap),
            y,
            button_width,
            button_height
        )

        hovered = rect.collidepoint(
            mouse_pos
        )

        background = (
            GOLD_DARK
            if hovered
            else WOOD_DARK
        )

        pygame.draw.rect(
            surface,
            background,
            rect,
            border_radius=10
        )

        pygame.draw.rect(
            surface,
            GOLD,
            rect,
            width=3,
            border_radius=10
        )

        image = button_font.render(
            text,
            True,
            color
        )

        surface.blit(
            image,
            image.get_rect(
                center=rect.center
            )
        )

        whist_button_rects.append(
            (rect, text)
        )

    text = font.render(
        "Выберите действие",
        True,
        IVORY
    )

    surface.blit(
        text,
        text.get_rect(
            center=(
                WIDTH // 2,
                500
            )
        )
    )

def draw_whist_done(surface):

    if game_phase != "whist_done":
        return

    title_font = pygame.font.SysFont(
        "Georgia",
        64,
        bold=True
    )

    text_font = pygame.font.SysFont(
        "Georgia",
        42,
        bold=True
    )

    title = title_font.render(
        "РЕШЕНИЕ ПРИНЯТО",
        True,
        GOLD
    )

    surface.blit(
        title,
        title.get_rect(
            center=(
                WIDTH // 2,
                220
            )
        )
    )

    text = text_font.render(
        whist_choice,
        True,
        IVORY
    )

    surface.blit(
        text,
        text.get_rect(
            center=(
                WIDTH // 2,
                320
            )
        )
    )

# ============================================================
# ТОРГОВЛЯ
# ============================================================

def get_bid_value(bid):

    if bid == "":
        return -1

    if bid in ("Пас", "Мизер"):
        return -1

    if bid == "Мизер":
        return 14.5

    suit_order = {
        "♠": 0,
        "♣": 1,
        "♦": 2,
        "♥": 3,
        "БК": 4
    }

    if bid.endswith("БК"):
        level = int(bid[:-2])
        suit = "БК"
    else:
        level = int(bid[:-1])
        suit = bid[-1]

    return (level - 6) * 5 + suit_order[suit]


def get_available_bids(player):

    available = []

    highest_value = get_bid_value(
        highest_bid
    )

    for bid in BID_OPTIONS:

        if bid == "Пас":
            available.append(bid)
            continue

        if bid == "Мизер":

            if (
                player_bids[player] == ""
                and highest_bid == ""
            ):

                available.append(bid)

            continue

        if highest_bid == "Мизер":

            if get_bid_value(bid) >= get_bid_value("9♠"):

                available.append(bid)

            continue

        if get_bid_value(bid) > highest_value:

            available.append(bid)

    return available


def get_available_contracts():

    available = []

    current_value = get_bid_value(
        highest_bid
    )

    for bid in BID_OPTIONS:

        if bid == "Пас":
            continue

        if get_bid_value(bid) >= current_value:
            available.append(bid)

    return available


def get_card_rank_value(rank):

    rank_values = {
        "7": 0,
        "8": 1,
        "9": 2,
        "10": 3,
        "В": 4,
        "Д": 5,
        "К": 6,
        "Т": 7
    }

    return rank_values[rank]


def get_bid_contract(bid):

    if bid == "Мизер":
        return "Мизер", None

    if bid.endswith("БК"):

        level = int(bid[:-2])

        return "БК", level

    level = int(bid[:-1])
    suit = bid[-1]

    return suit, level


def card_strength(rank):

    values = {
        "7": 0,
        "8": 1,
        "9": 2,
        "10": 3,
        "В": 4,
        "Д": 5,
        "К": 6,
        "Т": 7
    }

    return values[rank]


def analyze_hand_for_contract(hand, contract):

    suit, level = get_bid_contract(contract)

    if suit == "Мизер":

        return analyze_misere_hand(hand)

    if suit == "БК":

        return analyze_no_trump_hand(hand, level)

    return analyze_suit_hand(
        hand,
        suit,
        level
    )


def analyze_suit_hand(hand, trump, level):

    score = 0

    trump_cards = []
    side_cards = []

    suit_counts = {
        "♠": 0,
        "♣": 0,
        "♦": 0,
        "♥": 0
    }

    for rank, suit in hand:

        suit_counts[suit] += 1

        if suit == trump:

            trump_cards.append(rank)

        else:

            side_cards.append(
                (rank, suit)
            )

    # --------------------------------------------------------
    # Сила козырной масти
    # --------------------------------------------------------

    for rank in trump_cards:

        value = card_strength(rank)

        score += value * 1.6

        if rank == "Т":

            score += 6

        elif rank == "К":

            score += 3

        elif rank == "Д":

            score += 1

    # --------------------------------------------------------
    # Длина козыря
    # --------------------------------------------------------

    trump_length = len(trump_cards)

    if trump_length >= 5:

        score += 7

    elif trump_length == 4:

        score += 4

    elif trump_length == 3:

        score += 1

    # --------------------------------------------------------
    # Старшие карты в других мастях
    # --------------------------------------------------------

    for rank, suit in side_cards:

        if rank == "Т":

            score += 4

        elif rank == "К":

            score += 1.5

        elif rank == "Д":

            score += 0.5

    # --------------------------------------------------------
    # Длинные побочные масти
    # --------------------------------------------------------

    for suit_name in suit_counts:

        if suit_name == trump:

            continue

        count = suit_counts[suit_name]

        if count >= 5:

            score += 2

        elif count == 4:

            score += 1

    # --------------------------------------------------------
    # Чем выше контракт, тем больше требуется силы.
    #
    # Это НЕ означает автоматический отказ.
    # Это лишь увеличивает необходимый порог.
    # --------------------------------------------------------

    required = {
        6: 20,
        7: 27,
        8: 34,
        9: 41,
        10: 48
    }

    target = required.get(
        level,
        48
    )

    # --------------------------------------------------------
    # Запас силы относительно требуемого уровня.
    # --------------------------------------------------------

    confidence = score - target

    return confidence


def analyze_no_trump_hand(hand, level):

    score = 0

    suit_counts = {
        "♠": 0,
        "♣": 0,
        "♦": 0,
        "♥": 0
    }

    for rank, suit in hand:

        suit_counts[suit] += 1

        if rank == "Т":

            score += 7

        elif rank == "К":

            score += 3

        elif rank == "Д":

            score += 1

        elif rank == "В":

            score += 0.3

    # --------------------------------------------------------
    # В БК длина масти менее важна,
    # но наличие нескольких карт одной масти
    # всё равно помогает контролировать масть.
    # --------------------------------------------------------

    for suit in suit_counts:

        count = suit_counts[suit]

        if count >= 5:

            score += 2

        elif count == 4:

            score += 1

    required = {
        6: 25,
        7: 32,
        8: 39,
        9: 46,
        10: 53
    }

    target = required.get(
        level,
        53
    )

    return score - target


def analyze_misere_hand(hand):

    score = 0

    # --------------------------------------------------------
    # Для мизера нужны слабые карты.
    #
    # Чем больше мелких карт и коротких мастей,
    # тем лучше.
    # --------------------------------------------------------

    suit_counts = {
        "♠": 0,
        "♣": 0,
        "♦": 0,
        "♥": 0
    }

    for rank, suit in hand:

        suit_counts[suit] += 1

        value = card_strength(rank)

        # Маленькая карта полезна для мизера.
        score += (
            7 - value
        )

    # --------------------------------------------------------
    # Короткие масти позволяют легче избавляться
    # от опасных карт.
    # --------------------------------------------------------

    for suit in suit_counts:

        count = suit_counts[suit]

        if count == 1:

            score += 4

        elif count == 2:

            score += 2

    # --------------------------------------------------------
    # Старшие карты особенно опасны.
    # --------------------------------------------------------

    for rank, suit in hand:

        if rank == "Т":

            score -= 7

        elif rank == "К":

            score -= 4

        elif rank == "Д":

            score -= 2

    return score


def estimate_bid_confidence(hand, bid):

    # --------------------------------------------------------
    # Оцениваем конкретную заявку.
    #
    # Результат:
    #
    # положительный → заявка выглядит реалистично
    # отрицательный → заявка рискованна
    # --------------------------------------------------------

    return analyze_hand_for_contract(
        hand,
        bid
    )


def estimate_best_bid(hand):

    # --------------------------------------------------------
    # Эта функция теперь не принимает решение сама.
    #
    # Она оставлена как совместимость со старым кодом.
    # Реальное решение будет принимать choose_bot_bid().
    # --------------------------------------------------------

    best_bid = None
    best_confidence = -999

    for bid in BID_OPTIONS:

        if bid == "Пас":

            continue

        confidence = estimate_bid_confidence(
            hand,
            bid
        )

        if confidence > best_confidence:

            best_confidence = confidence
            best_bid = bid

    if best_bid is None:

        return None

    return best_bid

def get_unknown_cards(hand):

    deck = create_deck()

    known_cards = set(hand)

    return [
        card
        for card in deck
        if card not in known_cards
    ]


def choose_discard_for_simulation(cards, contract):

    suit, level = get_bid_contract(contract)

    # --------------------------------------------------------
    # Мизер:
    # стараемся избавиться от самых старших карт.
    # --------------------------------------------------------

    if suit == "Мизер":

        sorted_cards = sorted(
            cards,
            key=lambda card: card_strength(card[0]),
            reverse=True
        )

        return sorted_cards[:2]

    # --------------------------------------------------------
    # Игра в масти:
    # сохраняем козырь, избавляемся от слабых
    # побочных карт.
    # --------------------------------------------------------

    if suit in ("♠", "♣", "♦", "♥"):

        discard_candidates = [
            card
            for card in cards
            if card[1] != suit
        ]

        discard_candidates.sort(
            key=lambda card: card_strength(card[0])
        )

        if len(discard_candidates) >= 2:

            return discard_candidates[:2]

        remaining = sorted(
            cards,
            key=lambda card: card_strength(card[0])
        )

        return remaining[:2]

    # --------------------------------------------------------
    # БК:
    # избавляемся от самых слабых карт.
    # --------------------------------------------------------

    sorted_cards = sorted(
        cards,
        key=lambda card: card_strength(card[0])
    )

    return sorted_cards[:2]


def card_beats(
    card,
    winning_card,
    lead_suit,
    trump
):

    rank, suit = card
    winning_rank, winning_suit = winning_card

    # Козырь всегда бьёт некозырную карту.
    if trump is not None:

        if suit == trump and winning_suit != trump:

            return True

        if (
            winning_suit == trump
            and suit != trump
        ):

            return False

    # Карта другой масти не может перебить
    # карту масти хода.
    if suit != winning_suit:

        return False

    return (
        card_strength(rank)
        > card_strength(winning_rank)
    )


def choose_simulated_card(
    hand,
    lead_suit,
    winning_card,
    trump,
    is_declarer
):

    # --------------------------------------------------------
    # Первый ход взятки.
    #
    # Разыгрывающий старается сначала использовать
    # сильные побочные карты, особенно Тузы.
    #
    # Если Туза нет — выбирает сильную карту
    # из самой длинной побочной масти.
    # --------------------------------------------------------

    if winning_card is None:

        if is_declarer:

            aces = [
                card
                for card in hand
                if card[0] == "Т"
                and (
                    trump is None
                    or card[1] != trump
                )
            ]

            if aces:
                return aces[0]

            suit_groups = {}

            for card in hand:

                if (
                    trump is not None
                    and card[1] == trump
                ):
                    continue

                suit_groups.setdefault(
                    card[1],
                    []
                ).append(card)

            if suit_groups:

                longest_suit = max(
                    suit_groups,
                    key=lambda suit: len(
                        suit_groups[suit]
                    )
                )

                return max(
                    suit_groups[longest_suit],
                    key=lambda card: card_strength(
                        card[0]
                    )
                )

        # ----------------------------------------------------
        # Защитник.
        #
        # Начинаем с сильной карты побочной масти,
        # стараясь не выбрасывать козырь первым ходом.
        # ----------------------------------------------------

        non_trumps = [
            card
            for card in hand
            if (
                trump is None
                or card[1] != trump
            )
        ]

        if non_trumps:

            return max(
                non_trumps,
                key=lambda card: card_strength(
                    card[0]
                )
            )

        return max(
            hand,
            key=lambda card: card_strength(
                card[0]
            )
        )

    # --------------------------------------------------------
    # Сначала обязательно идём в масть хода.
    # --------------------------------------------------------

    same_suit = [
        card
        for card in hand
        if card[1] == lead_suit
    ]

    if same_suit:

        beating_cards = [
            card
            for card in same_suit
            if card_beats(
                card,
                winning_card,
                lead_suit,
                trump
            )
        ]

        # ----------------------------------------------------
        # Разыгрывающий.
        #
        # Если можно взять взятку —
        # берём минимальной картой.
        #
        # Если взять нельзя — отдаём минимальную.
        # ----------------------------------------------------

        if is_declarer:

            if beating_cards:

                return min(
                    beating_cards,
                    key=lambda card: card_strength(
                        card[0]
                    )
                )

            return min(
                same_suit,
                key=lambda card: card_strength(
                    card[0]
                )
            )

        # ----------------------------------------------------
        # Защитник.
        #
        # Защитник тоже старается взять взятку,
        # но если уже понятно, что карта не перебивается,
        # отдаёт минимальную.
        # ----------------------------------------------------

        if beating_cards:

            return min(
                beating_cards,
                key=lambda card: card_strength(
                    card[0]
                )
            )

        return min(
            same_suit,
            key=lambda card: card_strength(
                card[0]
            )
        )

    # --------------------------------------------------------
    # Масти хода нет.
    #
    # Ищем козырь.
    # --------------------------------------------------------

    if trump is not None:

        trumps = [
            card
            for card in hand
            if card[1] == trump
        ]

        if trumps:

            beating_trumps = [
                card
                for card in trumps
                if card_beats(
                    card,
                    winning_card,
                    lead_suit,
                    trump
                )
            ]

            if beating_trumps:

                return min(
                    beating_trumps,
                    key=lambda card: card_strength(
                        card[0]
                    )
                )

            # Если козырем взять нельзя,
            # всё равно скидываем минимальный козырь.
            return min(
                trumps,
                key=lambda card: card_strength(
                    card[0]
                )
            )

    # --------------------------------------------------------
    # Нечем брать и масти хода нет.
    #
    # Сбрасываем самую слабую карту.
    # --------------------------------------------------------

    return min(
        hand,
        key=lambda card: card_strength(
            card[0]
        )
    )


def simulate_contract(
    hand,
    contract,
    unknown_cards
):

    # --------------------------------------------------------
    # Получаем возможный прикуп.
    #
    # Бот его НЕ знает.
    # Это одна случайная гипотеза.
    # --------------------------------------------------------

    cards = unknown_cards.copy()

    random.shuffle(cards)

    talon_simulated = cards[:2]

    remaining = cards[2:]

    # --------------------------------------------------------
    # Бот гипотетически получает прикуп.
    # --------------------------------------------------------

    expanded_hand = (
        hand
        + talon_simulated
    )

    discard = choose_discard_for_simulation(
        expanded_hand,
        contract
    )

    final_hand = expanded_hand.copy()

    for card in discard:

        final_hand.remove(card)

    # --------------------------------------------------------
    # Раздаём остальные карты двум защитникам.
    # --------------------------------------------------------

    random.shuffle(remaining)

    opponent_1 = remaining[:10]
    opponent_2 = remaining[10:20]

    players = [
        final_hand,
        opponent_1,
        opponent_2
    ]

    suit, level = get_bid_contract(contract)

    if suit == "БК" or suit == "Мизер":

        trump = None

    else:

        trump = suit

    # --------------------------------------------------------
    # Игрок 0 — разыгрывающий.
    # Первым начинает он.
    # --------------------------------------------------------

    leader = 0
    declarer_tricks = 0

    for _ in range(10):

        played = []

        winning_card = None
        winner = leader
        lead_suit = None

        # ----------------------------------------------------
        # Три карты одной взятки.
        # ----------------------------------------------------

        for offset in range(3):

            player = (
                leader + offset
            ) % 3

            player_hand = players[player]

            card = choose_simulated_card(
                player_hand,
                lead_suit,
                winning_card,
                trump,
                player == 0
            )

            player_hand.remove(card)

            if lead_suit is None:

                lead_suit = card[1]

            if winning_card is None:

                winning_card = card
                winner = player

            elif card_beats(
                card,
                winning_card,
                lead_suit,
                trump
            ):

                winning_card = card
                winner = player

            played.append(card)

        # ----------------------------------------------------
        # Кто взял взятку — тот начинает следующую.
        # ----------------------------------------------------

        leader = winner

        if winner == 0:

            declarer_tricks += 1

    return declarer_tricks


def estimate_contract_probability(
    hand,
    contract,
    simulations=120
):

    unknown_cards = get_unknown_cards(hand)

    successful = 0
    total_tricks = 0

    suit, level = get_bid_contract(contract)

    for _ in range(simulations):

        tricks = simulate_contract(
            hand,
            contract,
            unknown_cards
        )

        total_tricks += tricks

        # ----------------------------------------------------
        # Для обычной игры нужно выполнить
        # количество взяток, соответствующее уровню.
        # ----------------------------------------------------

        if suit == "Мизер":

            if tricks == 0:

                successful += 1

        else:

            required_tricks = level

            if tricks >= required_tricks:

                successful += 1

    probability = (
        successful
        / simulations
    )

    average_tricks = (
        total_tricks
        / simulations
    )

    return probability, average_tricks

def choose_bot_bid(
    player,
    available_bids,
    history
):

    # --------------------------------------------------------
    # Доцент видит только собственную руку.
    # --------------------------------------------------------

    hand = player_hands[player]

    if len(available_bids) == 1:

        return "Пас"

    # --------------------------------------------------------
    # Проверяем каждую доступную заявку
    # через случайные возможные раздачи.
    # --------------------------------------------------------

    evaluations = []

    for bid in available_bids:

        if bid == "Пас":

            continue

        probability, average_tricks = (
            estimate_contract_probability(
                hand,
                bid,
                120
            )
        )

        evaluations.append(
            (
                bid,
                probability,
                average_tricks
            )
        )

    if not evaluations:

        return "Пас"

    # --------------------------------------------------------
    # Для отладки пока показываем,
    # что именно "думает" ИИ.
    # --------------------------------------------------------

    print()
    print(
        "ИИ:",
        player,
        hand
    )

    for bid, probability, average_tricks in evaluations:

        print(
            bid,
            "успех:",
            round(probability * 100, 1),
            "%",
            "средние взятки:",
            round(average_tricks, 2)
        )

    # --------------------------------------------------------
    # Выбираем заявку.
    #
    # Сначала рассматриваем только те,
    # где вероятность выполнения не меньше 55%.
    # --------------------------------------------------------

    reasonable = [
        item
        for item in evaluations
        if (
            item[1] >= 0.50
            if item[0] == "Мизер"
            else item[1] >= 0.45
        )
    ]

    if not reasonable:

        return "Пас"

    # --------------------------------------------------------
    # Из достаточно надёжных заявок выбираем
    # самую высокую по торговле.
    # --------------------------------------------------------

    reasonable.sort(
        key=lambda item: get_bid_value(item[0])
    )

    return reasonable[-1][0]

def bot_ai_worker(
    player,
    hand,
    available_bids,
    history
):

    global bot_result
    global bot_result_player

    # --------------------------------------------------------
    # ИИ работает только с копией руки.
    #
    # Pygame и состояние игры здесь не используются.
    # --------------------------------------------------------

    result = choose_bot_bid(
        player,
        available_bids,
        history
    )

    bot_result = result
    bot_result_player = player


def bot_make_bid(player):

    global current_bidder
    global bidding_active
    global bidding_finished
    global highest_bid
    global player_bids
    global opponent_actions
    global bid_history

    global bot_thinking
    global bot_result
    global bot_result_player

    # --------------------------------------------------------
    # Если ИИ уже думает — ничего больше не запускаем.
    # --------------------------------------------------------

    if bot_thinking:

        # ----------------------------------------------------
        # Проверяем, закончил ли поток расчёт.
        # ----------------------------------------------------

        if (
            bot_result is None
            or bot_result_player != player
        ):

            return

        # ----------------------------------------------------
        # ИИ закончил думать.
        # Забираем результат.
        # ----------------------------------------------------

        bid = bot_result

        bot_result = None
        bot_result_player = None
        bot_thinking = False

        # ----------------------------------------------------
        # Запоминаем заявку.
        # ----------------------------------------------------

        player_bids[player] = bid

        bid_history.append(
            (player, bid)
        )

        # ----------------------------------------------------
        # Показываем заявку над картами соперника.
        # ----------------------------------------------------

        if player == 1:

            opponent_actions[0] = bid

        elif player == 2:

            opponent_actions[1] = bid

        # ----------------------------------------------------
        # Обновляем текущую заявку.
        # ----------------------------------------------------

        if bid != "Пас":

            highest_bid = bid

        next_bidder()

        return

    # --------------------------------------------------------
    # Новый расчёт.
    # --------------------------------------------------------

    available_bids = get_available_bids(player)

    # --------------------------------------------------------
    # Если вариантов уже нет — Пас.
    # --------------------------------------------------------

    if len(available_bids) == 1:

        player_bids[player] = "Пас"

        bid_history.append(
            (player, "Пас")
        )

        if player == 1:

            opponent_actions[0] = "Пас"

        elif player == 2:

            opponent_actions[1] = "Пас"

        next_bidder()

        return

    # --------------------------------------------------------
    # Делаем копию руки.
    #
    # Поток ИИ не будет обращаться к игровой руке напрямую.
    # --------------------------------------------------------

    hand = player_hands[player].copy()
    available_bids = available_bids.copy()
    history = bid_history.copy()

    # --------------------------------------------------------
    # Сбрасываем старый результат.
    # --------------------------------------------------------

    bot_result = None
    bot_result_player = None

    bot_thinking = True

    # --------------------------------------------------------
    # Запускаем мозг ИИ отдельно от Pygame.
    # --------------------------------------------------------

    thread = threading.Thread(
        target=bot_ai_worker,
        args=(
            player,
            hand,
            available_bids,
            history
        ),
        daemon=True
    )

    thread.start()

def start_talon_phase():

    global game_phase
    global declarer
    global declarer_contract

    # --------------------------------------------------------
    # Находим победителя торговли.
    # --------------------------------------------------------

    declarer = None

    for player in range(3):

        if player_bids[player] == highest_bid:

            declarer = player
            break

    if declarer is None:
        return

    declarer_contract = highest_bid

    game_phase = "talon"


def next_bidder():

    global current_bidder
    global bidding_active
    global bidding_finished

    # --------------------------------------------------------
    # Сколько игроков ещё не сказали Пас
    # --------------------------------------------------------

    active_players = sum(
        1
        for bid in player_bids
        if bid != "Пас"
        and bid != ""
    )

    # --------------------------------------------------------
    # Если все трое сделали первые заявки
    # --------------------------------------------------------

    if all(bid != "" for bid in player_bids):

        # Все трое спасовали
        if highest_bid == "":

            bidding_active = False
            bidding_finished = True
            return

        # Если двое уже спасовали —
        # остаётся один победитель торговли
        pass_count = player_bids.count("Пас")

        if pass_count >= 2:

            bidding_active = False
            bidding_finished = True

            start_talon_phase()

            return

    # --------------------------------------------------------
    # Переходим к следующему игроку
    # --------------------------------------------------------

    current_bidder = (current_bidder + 1) % 3

    # --------------------------------------------------------
    # Пропускаем игроков, которые уже спасовали
    # --------------------------------------------------------

    while player_bids[current_bidder] == "Пас":

        current_bidder = (current_bidder + 1) % 3


def player_make_bid(bid):

    global highest_bid
    global player_bids

    if not bidding_active:
        return

    if current_bidder != 0:
        return

    # --------------------------------------------------------
    # Проверяем, действительно ли эта заявка разрешена
    # --------------------------------------------------------

    available_bids = get_available_bids(0)

    if bid not in available_bids:
        return

    player_bids[0] = bid

    bid_history.append(
        (0, bid)
    )

    if bid != "Пас":

        highest_bid = bid

    next_bidder()


def player_make_contract(contract):

    global declarer_contract
    global game_phase

    if game_phase != "contract":
        return

    if declarer != 0:
        return

    available_contracts = get_available_contracts()

    if contract not in available_contracts:
        return

    declarer_contract = contract

    global whist_current_player
    global whist_actions

    whist_current_player = (
        declarer + 1
    ) % 3

    whist_actions = ["", ""]

    game_phase = "whist"

def start_play_phase():

    global game_phase
    global play_current_player
    global trick_cards
    global trick_lead_suit
    global trick_winner
    global trick_number
    global played_cards

    play_current_player = declarer

    trick_cards = []

    played_cards = []

    trick_lead_suit = None

    trick_winner = None

    trick_number = 1

    game_phase = "play"

    print(
        "РОЗЫГРЫШ: начало",
        "| разыгрывающий:",
        declarer,
        "| контракт:",
        declarer_contract
    )

def bot_make_play():

    global play_current_player
    global trick_cards
    global played_cards

    if game_phase != "play":
        return

    if play_current_player == 0:
        return

    player = play_current_player

    if not player_hands[player]:
        return

    card = player_hands[player][0]

    print(
        "РОЗЫГРЫШ: ИИ",
        player,
        "сыграл:",
        card
    )

    trick_cards.append(
        (player, card)
    )

    played_cards.append(
        (player, card)
    )

    player_hands[player].remove(
        card
    )

    play_current_player = (
        play_current_player + 1
    ) % 3

def draw_talon_phase(surface):

    if game_phase != "talon":
        return

    # --------------------------------------------------------
    # Заголовок
    # --------------------------------------------------------

    title = pygame.font.SysFont("roboto", 96).render(
        "ПРИКУП",
        True,
        GOLD
    )

    surface.blit(
        title,
        title.get_rect(
            center=(
                WIDTH // 2,
                210
            )
        )
    )

    # --------------------------------------------------------
    # Если прикуп принадлежит нам —
    # показываем две карты.
    # --------------------------------------------------------

    if declarer == 0:

        card_gap = 30

        total_width = (
            CARD_W * 2
            + card_gap
        )

        start_x = (
            WIDTH // 2
            - total_width // 2
        )

        y = 320

        for index, card in enumerate(talon):

            rect = pygame.Rect(
                start_x
                + index * (CARD_W + card_gap),
                y,
                CARD_W,
                CARD_H
            )

            draw_card_face(
                surface,
                rect,
                card[0],
                card[1]
            )


    else:

        names = [
            "ВАШ",
            "Студента",
            "Доцента"
        ]

        text = font.render(
            f"Прикуп у {names[declarer]}",
            True,
            IVORY
        )

        surface.blit(
            text,
            text.get_rect(
                center=(
                    WIDTH // 2,
                    390
                )
            )
        )

def take_talon():

    global game_phase
    global talon_taken
    global player_hands

    if game_phase != "talon":
        return

    if declarer != 0:
        return

    if talon_taken:
        return

    # --------------------------------------------------------
    # Забираем обе карты прикупа в нашу руку.
    # --------------------------------------------------------

    player_hands[0].extend(talon)

    # --------------------------------------------------------
    # Сортируем руку.
    # --------------------------------------------------------

    suit_order = {
        "♠": 0,
        "♣": 1,
        "♦": 2,
        "♥": 3
    }

    rank_order = {
        "7": 0,
        "8": 1,
        "9": 2,
        "10": 3,
        "В": 4,
        "Д": 5,
        "К": 6,
        "Т": 7
    }

    player_hands[0].sort(
        key=lambda card: (
            suit_order[card[1]],
            rank_order[card[0]]
        )
    )

    # --------------------------------------------------------
    # Прикуп больше не показываем.
    # --------------------------------------------------------

    talon_taken = True

    # --------------------------------------------------------
    # Следующий этап.
    # Пока временно возвращаемся к игре.
    # Снос сделаем следующим шагом.
    # --------------------------------------------------------

    game_phase = "discard"

def draw_bidding_window(surface, mouse_pos):

    global bid_buttons

    bid_buttons = []

    if (
        not bidding_active
        and game_phase != "contract"
    ):
        return

    # ----------------------------------------------------
    # Размер окна
    # ----------------------------------------------------

    window_width = 865
    window_height = 320

    window_rect = pygame.Rect(
        WIDTH // 2 - window_width // 2 + 52,
        HEIGHT // 2 - window_height // 2 - 70,
        window_width,
        window_height
    )

    # ----------------------------------------------------
    # Фон таблицы
    # ----------------------------------------------------

    pygame.draw.rect(
        surface,
        (150, 150, 150),
        window_rect,
        border_radius=12
    )

    pygame.draw.rect(
        surface,
        GOLD,
        window_rect,
        width=2,
        border_radius=12
    )

    # ----------------------------------------------------
    # Информация о ходе
    # ----------------------------------------------------

    if game_phase == "contract":

        turn_text = "Ваш окончательный заказ"

    elif current_bidder == 0:

        turn_text = "Ваш ход"

    else:

        names = [
            "ВАШ",
            "Студента",
            "Доцента"
        ]

        turn_text = f"Ход {names[current_bidder]}"

    turn_image = font.render(
        turn_text,
        True,
        BLACK
    )

    surface.blit(
        turn_image,
        turn_image.get_rect(
            center=(
                window_rect.centerx,
                window_rect.top + 30
            )
        )
    )

    # ----------------------------------------------------
    # Текущая заявка
    # ----------------------------------------------------

    if game_phase == "contract":

        current_text = (
            "Торговля выиграна: "
            + highest_bid
        )

    else:

        current_text = (
            "Текущая заявка: "
            + (highest_bid if highest_bid else "нет")
        )

    normal_font = pygame.font.SysFont(
        "Georgia",
        50,
        bold=True
    )

    suit_font = pygame.font.SysFont(
        "DejaVu Sans",
        80,
        bold=True
    )

    suit_colors = {
        "♠": BLACK,
        "♣": BLACK,
        "♦": RED,
        "♥": RED
    }

    parts = []

    for char in current_text:

        if char in suit_colors:

            image = suit_font.render(
                char,
                True,
                suit_colors[char]
            )

        else:

            image = normal_font.render(
                char,
                True,
                BLACK
            )

        parts.append(image)

    total_width = sum(
        image.get_width()
        for image in parts
    )

    current_x = (
        window_rect.centerx
        - total_width // 2
    )

    for image in parts:

        image_rect = image.get_rect(
            midleft=(
                current_x,
                window_rect.top + 65
            )
        )

        surface.blit(
            image,
            image_rect
        )

        current_x += image.get_width()

    # ----------------------------------------------------
    # Если сейчас ход бота — кнопки не показываем
    # ----------------------------------------------------

    if (
        game_phase == "bidding"
        and current_bidder != 0
    ):
        return

    # ----------------------------------------------------
    # Настройки кнопок
    # ----------------------------------------------------

    button_height = 46
    gap = 8
    button_padding = 20

    # ----------------------------------------------------
    # Раскладываем заявки по строкам
    # ----------------------------------------------------

    rows = []

    if game_phase == "contract":

        options_source = get_available_contracts()

    else:

        available_bids = get_available_bids(
        	0

        )

        options_source = [
        	bid
        	for bid in BID_OPTIONS
        	if bid in available_bids
        ]

    current_row = []
    current_width = 0

    available_width = (
        window_rect.width
        - button_padding * 2
    )

    for bid in options_source:

        text_width = 0

        for char in bid:

            if char in ("♠", "♣", "♦", "♥"):

                image = BID_SUIT_FONT.render(
                    char,
                    True,
                    BLACK
                )

            else:

                image = BID_TEXT_FONT.render(
                    char,
                    True,
                    BLACK
                )

            text_width += image.get_width()

        bid_width = (
            text_width
            + button_padding * 2
            - 5
        )

        if (
            current_row
            and current_width
            + gap
            + bid_width
            > available_width
        ):

            rows.append(current_row)

            current_row = []
            current_width = 0

        if current_row:

            current_width += gap

        current_row.append(bid)
        current_width += bid_width

    if current_row:

        rows.append(current_row)

    # ----------------------------------------------------
    # Рисуем строки
    # ----------------------------------------------------

    start_y = window_rect.top + 100

    for row_index, options in enumerate(rows):

        button_widths = []

        for bid in options:

            text_width = 0

            for char in bid:

                if char in ("♠", "♣", "♦", "♥"):

                    image = BID_SUIT_FONT.render(
                        char,
                        True,
                        BLACK
                    )

                else:

                    image = BID_TEXT_FONT.render(
                        char,
                        True,
                        BLACK
                    )

                text_width += image.get_width()

            button_widths.append(
                text_width + button_padding * 2
            )

        row_width = (
            sum(button_widths)
            + (len(options) - 1) * gap
        )

        start_x = (
            window_rect.centerx
            - row_width // 2
        )

        row_y = (
            start_y
            + row_index * (button_height + gap)
        )

        current_x = start_x

        for index, bid in enumerate(options):

            button_width = button_widths[index]

            rect = pygame.Rect(
                current_x,
                row_y,
                button_width,
                button_height
            )

            hovered = rect.collidepoint(
                mouse_pos
            )

            if hovered:

                pygame.draw.rect(
                    surface,
                    BID_BUTTON_HOVER,
                    rect,
                    border_radius=8
                )

            else:

                pygame.draw.rect(
                    surface,
                    BID_BUTTON,
                    rect,
                    border_radius=8
                )

            pygame.draw.rect(
                surface,
                GOLD,
                rect,
                width=2,
                border_radius=8
            )

            suit_colors = {
                "♠": BLACK,
                "♣": BLACK,
                "♦": RED,
                "♥": RED
            }

            parts = []
            total_width = 0

            for char in bid:

                if char in suit_colors:

                    image = BID_SUIT_FONT.render(
                        char,
                        True,
                        suit_colors[char]
                    )

                else:

                    image = BID_TEXT_FONT.render(
                        char,
                        True,
                        BLACK
                    )

                parts.append(image)

                total_width += image.get_width()

            x = (
                rect.centerx
                - total_width // 2
            )

            for image in parts:

                y = (
                    rect.centery
                    - image.get_height() // 2
                )

                surface.blit(
                    image,
                    (x, y)
                )

                x += image.get_width()

            bid_buttons.append(
                (rect, bid)
            )

            current_x += (
                button_width
                + gap
            )


# ============================================================
# КНОПКА
# ============================================================

def draw_button(
    surface,
    rect,
    text,
    text_color,
    hovered
):

    # --------------------------------------------------------
    # Фон кнопки
    # --------------------------------------------------------

    if hovered:

        pygame.draw.rect(
            surface,
            GOLD_DARK,
            rect,
            border_radius=8
        )

    else:

        pygame.draw.rect(
            surface,
            WOOD_DARK,
            rect,
            border_radius=8
        )

    # Рамка

    pygame.draw.rect(
        surface,
        GOLD,
        rect,
        width=2,
        border_radius=8
    )

    # --------------------------------------------------------
    # Шрифты
    # --------------------------------------------------------

    normal_font = pygame.font.SysFont(
        "Georgia",
        28,
        bold=True
    )

    suit_font = pygame.font.SysFont(
        "DejaVu Sans",
        30,
        bold=True
    )

    # --------------------------------------------------------
    # Цвета мастей
    # --------------------------------------------------------

    suit_colors = {
        "♠": BLACK,
        "♣": BLACK,
        "♦": RED,
        "♥": RED
    }

    # --------------------------------------------------------
    # Разбиваем надпись на символы
    # --------------------------------------------------------

    parts = []

    for char in text:

        if char in suit_colors:

            image = suit_font.render(
                char,
                True,
                suit_colors[char]
            )

        else:

            image = normal_font.render(
                char,
                True,
                text_color
            )

        parts.append(image)

    # --------------------------------------------------------
    # Общая ширина
    # --------------------------------------------------------

    total_width = sum(
        image.get_width()
        for image in parts
    )

    x = (
        rect.centerx
        - total_width // 2
    )

    # --------------------------------------------------------
    # Рисуем
    # --------------------------------------------------------

    for image in parts:

        image_rect = image.get_rect(
            midleft=(
                x,
                rect.centery
            )
        )

        surface.blit(
            image,
            image_rect
        )

        x += image.get_width()


# ============================================================
# ГЛАВНОЕ МЕНЮ
# ============================================================

def draw_interface(
    surface,
    mouse_pos
):

    title = title_font.render(
        "ПРЕФЕРАНС",
        True,
        GOLD
    )

    surface.blit(
        title,
        title.get_rect(
            center=(
                WIDTH // 2,
                78
            )
        )
    )

    # --------------------------------------------------------
    # ИГРАТЬ
    # --------------------------------------------------------

    play_rect = pygame.Rect(
        WIDTH // 2 - BUTTON_WIDTH // 2,
        212,
        BUTTON_WIDTH,
        BUTTON_HEIGHT
    )

    play_hovered = play_rect.collidepoint(
        mouse_pos
    )

    draw_button(
        surface,
        play_rect,
        "ИГРАТЬ",
        (
            GREEN_LIGHT
            if play_hovered
            else GREEN
        ),
        play_hovered
    )

    # --------------------------------------------------------
    # ВЫХОД
    # --------------------------------------------------------

    exit_rect = pygame.Rect(
        WIDTH // 2 - BUTTON_WIDTH // 2,
        HEIGHT - 285,
        BUTTON_WIDTH,
        BUTTON_HEIGHT
    )

    exit_hovered = exit_rect.collidepoint(
        mouse_pos
    )

    draw_button(
        surface,
        exit_rect,
        "ВЫХОД",
        (
            RED_LIGHT
            if exit_hovered
            else RED
        ),
        exit_hovered
    )

    return play_rect, exit_rect

def bot_make_whist():

    global whist_current_player
    global whist_actions
    global whist_choice
    global game_phase

    if game_phase != "whist":
        return

    if whist_current_player == 0:
        return

    player = whist_current_player

    print(
        "ВИСТ: ход ИИ",
        player,
        "| контракт:",
        declarer_contract,
        "| предыдущие решения:",
        whist_actions
    )

    hand = player_hands[player]

    suit, level = get_bid_contract(
        declarer_contract
    )
    print(
        "ВИСТ: ИИ",
        player,
        "| масть:",
        suit,
        "| уровень:",
        level
    )

    # --------------------------------------------------------
    # Мизер — особый контракт.
    # Пока не вистуем против мизера.
    # --------------------------------------------------------

    if suit == "Мизер":

        action = "ПАС"

    else:

        trump = (
            None
            if suit == "БК"
            else suit
        )

        score = 0

        # ----------------------------------------------------
        # Старшие карты
        # ----------------------------------------------------

        for rank, card_suit in hand:

            value = card_strength(rank)

            if rank == "Т":

                score += 4

            elif rank == "К":

                score += 2

            elif rank == "Д":

                score += 1

            elif rank == "В":

                score += 0.5

            # Козырные карты ценнее
            if (
                trump is not None
                and card_suit == trump
            ):

                score += value * 0.8

        # ----------------------------------------------------
        # Длина козыря
        # ----------------------------------------------------

        if trump is not None:

            trump_count = sum(
                1
                for rank, card_suit in hand
                if card_suit == trump
            )

            if trump_count >= 5:

                score += 4

            elif trump_count == 4:

                score += 2

            elif trump_count == 3:

                score += 1

        # ----------------------------------------------------
        # Чем выше контракт, тем сложнее вистовать.
        # ----------------------------------------------------

        if level == 6:

            threshold = 11

        elif level == 7:

            threshold = 9

        elif level == 8:

            threshold = 7

        else:

            threshold = 5

        if score >= threshold:

            action = "ВИСТ"

        else:

            action = "ПАС"

        # ----------------------------------------------------
        # Полвиста.
        # Если первый вистующий спасовал,
        # второй может выбрать полвиста для 6 или 7.
        # ----------------------------------------------------

        first_action = whist_actions[0]

        if (
            first_action == "ПАС"
            and level in (6, 7)
            and action == "ВИСТ"
        ):

            action = "ПОЛВИСТА"

    action_index = (
        whist_current_player
        - declarer
        - 1
    ) % 3

    print(
        "ВИСТ: ИИ",
        player,
        "| выбрал:",
        action,
        "| индекс:",
        action_index
    )

    whist_actions[action_index] = action

    whist_choice = action

    whist_current_player = (
        whist_current_player + 1
    ) % 3

    if all(
        value != ""
        for value in whist_actions
    ):

        whist_choice = whist_actions[0]

        start_play_phase()


# ============================================================
# ГЛАВНЫЙ ЦИКЛ
# ============================================================

def main():

    global WIDTH, HEIGHT, screen
    global game_started
    global game_phase
    global whist_current_player
    global play_current_player

    running = True

    # --------------------------------------------------------
    # Кнопки создаём заранее
    # --------------------------------------------------------

    play_rect = pygame.Rect(
        WIDTH // 2 - BUTTON_WIDTH // 2,
        212,
        BUTTON_WIDTH,
        BUTTON_HEIGHT
    )

    exit_rect = pygame.Rect(
        WIDTH // 2 - BUTTON_WIDTH // 2,
        HEIGHT - 285,
        BUTTON_WIDTH,
        BUTTON_HEIGHT
    )

    while running:



        # ----------------------------------------------------
        # События
        # ----------------------------------------------------

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                running = False

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    running = False

                elif event.key == pygame.K_F11:

                    pygame.display.toggle_fullscreen()

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:

                    # ----------------------------------------
                    # Торговля
                    # ----------------------------------------

                    if game_started and bidding_active:

                        for rect, bid in bid_buttons:

                            if rect.collidepoint(event.pos):

                                player_make_bid(bid)

                                break

                    # ----------------------------------------
                    # Получение прикупа
                    # ----------------------------------------

                    elif game_started and game_phase == "talon":

                        if declarer == 0:

                            take_talon()

                    elif game_started and game_phase == "contract":

                        for rect, contract in bid_buttons:

                            if rect.collidepoint(event.pos):

                                player_make_contract(
                                    contract
                                )

                                break

                    # ----------------------------------------
                    # Выбор карт для сноса
                    # ----------------------------------------
                    elif game_started and game_phase == "whist":

                        for rect, action in whist_button_rects:

                            if rect.collidepoint(event.pos):

                                action_index = (
                                    whist_current_player
                                    - declarer
                                    - 1
                                ) % 3

                                print(
                                    "ВИСТ: игрок 0 | выбрал:",
                                    action,
                                    "| индекс:",
                                    action_index
                                )

                                whist_actions[action_index] = action

                                whist_choice = action

                                whist_actions[action_index] = action
                                print(
                                    "ВИСТ: игрок 0 выбрал:",
                                    action,
                                    "| все решения:",
                                    whist_actions
                                )

                                print(
                                    "ВИСТ: игрок 0 выбрал:",
                                    action,
                                    "| все решения:",
                                    whist_actions
                                )

                                whist_choice = action

                                whist_current_player = (
                                    whist_current_player + 1
                                ) % 3

                                if all(
                                    value != ""
                                    for value in whist_actions
                                ):

                                    start_play_phase()

                                break

                    elif game_started and game_phase == "play":

                        if play_current_player == 0:

                            hand = player_hands[0]

                            same_suit_step = CARD_W
                            new_suit_gap = 18

                            total_width = 0

                            for index, card in enumerate(hand):

                                total_width += same_suit_step

                                if (
                                    index > 0
                                    and card[1] != hand[index - 1][1]
                                ):

                                    total_width += new_suit_gap

                            total_width -= same_suit_step

                            start_x = (
                                WIDTH // 2
                                - total_width // 2
                                - 60
                            )

                            y = HEIGHT - CARD_H - 55

                            current_x = start_x

                            for index, card in enumerate(hand):

                                if (
                                    index > 0
                                    and card[1] != hand[index - 1][1]
                                ):

                                    current_x += new_suit_gap

                                rect = pygame.Rect(
                                    current_x,
                                    y,
                                    CARD_W,
                                    CARD_H
                                )

                                if rect.collidepoint(event.pos):

                                    print(
                                        "РОЗЫГРЫШ: игрок 0 сыграл:",
                                        card
                                    )

                                    trick_cards.append(
                                        (0, card)
                                    )

                                    played_cards.append(
                                        (0, card)
                                    )

                                    player_hands[0].remove(
                                        card
                                    )

                                    play_current_player = 1

                                    break

                                current_x += same_suit_step


                    elif game_started and game_phase == "discard":

                        if (
                            len(discard_selection) == 2
                            and discard_button_rect is not None
                            and discard_button_rect.collidepoint(
                                event.pos
                            )
                        ):

                            player_hands[0] = [
                                card
                                for index, card in enumerate(
                                    player_hands[0]
                                )
                                if index not in discard_selection
                            ]

                            discard_selection.clear()

                            if declarer_contract == "Мизер":

                                game_phase = "whist"

                            else:

                                game_phase = "contract"

                            continue

                        hand = player_hands[0]

                        same_suit_step = CARD_W
                        new_suit_gap = 18

                        total_width = 0

                        for index, card in enumerate(hand):

                            total_width += same_suit_step

                            if (
                                index > 0
                                and card[1] != hand[index - 1][1]
                            ):

                                total_width += new_suit_gap

                        total_width -= same_suit_step

                        start_x = (
                            WIDTH // 2
                            - total_width // 2
                            - 60
                        )

                        y = HEIGHT - CARD_H - 55

                        current_x = start_x

                        for index, card in enumerate(hand):

                            if (
                                index > 0
                                and card[1] != hand[index - 1][1]
                            ):

                                current_x += new_suit_gap

                            card_y = y

                            if index in discard_selection:

                                card_y -= 25

                            rect = pygame.Rect(
                                current_x,
                                card_y,
                                CARD_W,
                                CARD_H
                            )

                            if rect.collidepoint(event.pos):

                                if index in discard_selection:

                                    discard_selection.remove(
                                        index
                                    )

                                elif len(discard_selection) < 2:

                                    discard_selection.append(
                                        index
                                    )

                                break

                            current_x += same_suit_step

                    # ----------------------------------------
                    # Главное меню
                    # ----------------------------------------

                    elif not game_started:

                        if play_rect.collidepoint(event.pos):

                            game_started = True

                            deal_cards()
                            start_bidding()

                        elif exit_rect.collidepoint(event.pos):

                            running = False

        mouse_pos = pygame.mouse.get_pos()


        # ----------------------------------------------------
        # Стол
        # ----------------------------------------------------

        draw_wood_table(screen)

        # ----------------------------------------------------
        # Подсвечники
        # ----------------------------------------------------

        draw_candelabra(
            screen,
            115,
            125,
            0.85
        )

        draw_candelabra(
            screen,
            WIDTH - 115,
            125,
            0.85
        )

        draw_candelabra(
            screen,
            115,
            HEIGHT - 135,
            0.75
        )

        draw_candelabra(
            screen,
            WIDTH - 115,
            HEIGHT - 135,
            0.75
        )

        # ----------------------------------------------------
        # Главное меню
        # ----------------------------------------------------

        if not game_started:

            draw_demo_cards(screen)

            draw_players(screen)

            play_rect, exit_rect = draw_interface(
                screen,
                mouse_pos
            )

        # ----------------------------------------------------
        # Игра
        # ----------------------------------------------------

        else:

            # Боты делают ход, когда наступает их очередь

            if bidding_active and current_bidder != 0:
            	bot_make_bid(current_bidder)

            if (
                game_phase == "whist"
                and whist_current_player != 0
            ):

                bot_make_whist()
            if (
                game_phase == "play"
                and play_current_player != 0
            ):

                bot_make_play()
            draw_game_cards(screen)
            draw_opponent_actions(screen)
            draw_player_action(screen)
            draw_players(screen)

            # ------------------------------------------------
            # Сыгранные карты на столе
            # ------------------------------------------------

            if game_phase == "play":

                for player, card in played_cards:

                    if player == 0:

                        card_x = (
                            WIDTH // 2
                            - CARD_W // 2
                        )

                        card_y = (
                            HEIGHT // 2
                            - CARD_H // 2
                        )

                    elif player == 1:

                        card_x = (
                            WIDTH // 2
                            - CARD_W // 2
                            - 150
                        )

                        card_y = (
                            HEIGHT // 2
                            - CARD_H // 2
                            - 80
                        )

                    else:

                        card_x = (
                            WIDTH // 2
                            - CARD_W // 2
                            + 150
                        )

                        card_y = (
                            HEIGHT // 2
                            - CARD_H // 2
                            - 80
                        )

                    card_rect = pygame.Rect(
                        card_x,
                        card_y,
                        CARD_W,
                        CARD_H
                    )

                    draw_card_face(
                        screen,
                        card_rect,
                        card[0],
                        card[1]
                    )

            if (
                game_phase == "bidding"
                or game_phase == "contract"
            ):
            	draw_bidding_window(
            		screen,
            		mouse_pos
            	)

            elif game_phase == "talon":
            	draw_talon_phase(screen)

            elif game_phase == "discard":
            	draw_discard_button(
            		screen,
            		mouse_pos
            	)

            elif game_phase == "discard_done":
            	draw_discard_done(screen)

            elif game_phase == "whist":
            	draw_whist_phase(
            		screen,
            		mouse_pos
            	)

            elif game_phase == "whist_done":
            	draw_whist_done(screen)

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()


# ============================================================
# ЗАПУСК
# ============================================================

if __name__ == "__main__":
    main()
