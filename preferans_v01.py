import math
import random
import threading
import pygame

# ------------------------------------------------------------
# Преферанс — версия 0.62
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

    text = player_bids[0]

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

    x = WIDTH // 2 - total_width // 2
    y = HEIGHT - CARD_H - 165

    padding_x = 20
    padding_y = 8

    background_rect = pygame.Rect(
        x - padding_x,
        y - padding_y,
        total_width + padding_x * 2,
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

    if opponent_actions[0]:

        text = opponent_actions[0]

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

    if opponent_actions[1]:

        text = opponent_actions[1]

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

        rect = pygame.Rect(
            current_x,
            y,
            CARD_W,
            CARD_H
        )

        draw_card_face(
            surface,
            rect,
            rank,
            suit
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

# ============================================================
# ТОРГОВЛЯ
# ============================================================

def get_bid_value(bid):

    if bid == "":
        return -1

    if bid == "Пас":
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

    # --------------------------------------------------------
    # Пас доступен всегда
    # --------------------------------------------------------

    available.append("Пас")

    # --------------------------------------------------------
    # Мизер можно объявить только первым заявлением
    # этого игрока и только если он ещё не торговался
    # --------------------------------------------------------

    if player_bids[player] == "":

        if highest_bid == "":

            available.append("Мизер")

    # --------------------------------------------------------
    # Обычные игры
    # --------------------------------------------------------

    current_value = get_bid_value(highest_bid)

    for bid in BID_OPTIONS:

        if bid in ("Пас", "Мизер"):
            continue

        if get_bid_value(bid) > current_value:

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
    # Если это первый ход взятки,
    # начинаем с самой сильной карты.
    # --------------------------------------------------------

    if winning_card is None:

        sorted_hand = sorted(
            hand,
            key=lambda card: card_strength(card[0]),
            reverse=True
        )

        return sorted_hand[0]

    # --------------------------------------------------------
    # Сначала обязательно пытаемся идти в масть.
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
        # Защита старается взять взятку,
        # если это возможно.
        #
        # Раздающий старается тратить
        # минимально необходимую карту.
        # ----------------------------------------------------

        if is_declarer:

            if beating_cards:

                return min(
                    beating_cards,
                    key=lambda card: card_strength(card[0])
                )

            return min(
                same_suit,
                key=lambda card: card_strength(card[0])
            )

        else:

            if beating_cards:

                return min(
                    beating_cards,
                    key=lambda card: card_strength(card[0])
                )

            return min(
                same_suit,
                key=lambda card: card_strength(card[0])
            )

    # --------------------------------------------------------
    # В масти хода нет.
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
                    key=lambda card: card_strength(card[0])
                )

            return min(
                trumps,
                key=lambda card: card_strength(card[0])
            )

    # --------------------------------------------------------
    # Нечем брать — отдаём самую слабую карту.
    # --------------------------------------------------------

    return min(
        hand,
        key=lambda card: card_strength(card[0])
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

def choose_bot_bid(player, available_bids):

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
        if item[1] >= 0.55
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
    available_bids
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
        available_bids
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
            available_bids
        ),
        daemon=True
    )

    thread.start()


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

    if bid != "Пас":

        highest_bid = bid

    next_bidder()

def draw_bidding_window(surface, mouse_pos):

    global bid_buttons

    bid_buttons = []

    if not bidding_active:
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

    if current_bidder == 0:

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

    if current_bidder != 0:
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

    columns = 7

    rows = []

    for i in range(0, len(BID_OPTIONS), columns):

        rows.append(
            BID_OPTIONS[i:i + columns]
        )

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


# ============================================================
# ГЛАВНЫЙ ЦИКЛ
# ============================================================

def main():

    global WIDTH, HEIGHT, screen
    global game_started

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
            draw_game_cards(screen)
            draw_opponent_actions(screen)
            draw_player_action(screen)
            draw_players(screen)
            draw_bidding_window(
                screen,
                mouse_pos
            )

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()


# ============================================================
# ЗАПУСК
# ============================================================

if __name__ == "__main__":
    main()
