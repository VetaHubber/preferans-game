import math
import random
import threading
import pygame

# ------------------------------------------------------------
# Преферанс — версия 0.636
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
# Кнопка выхода
# ------------------------------------------------------------

exit_button_rect = pygame.Rect(
    WIDTH - 55,
    40,
    55,
    55
)

exit_confirm = False

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

# ============================================================
# СОСТОЯНИЕ РАСПАСОВКИ
# ============================================================

raspasovka = False

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

trick_pause = False
trick_pause_start = 0

trick_animation = False
trick_animation_start = 0

# Прямоугольники кнопок торговли
bid_buttons = []

# ============================================================
# СОСТОЯНИЕ РАЗМЫШЛЕНИЯ ИИ
# ============================================================

bot_thinking = False
bot_result = None
bot_result_player = None
bot_result_probability = None
bot_previous_probability = [None, None, None]

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
# КНОПКА ВЫХОДА
# ============================================================

def draw_exit_button(surface):

    mouse_pos = pygame.mouse.get_pos()

    hovered = exit_button_rect.collidepoint(
        mouse_pos
    )

    # --------------------------------------------------------
    # Фон кнопки
    # --------------------------------------------------------

    button_color = (
        (155, 25, 22)
        if hovered
        else (110, 18, 16)
    )

    pygame.draw.circle(
        surface,
        (55, 30, 28),
        exit_button_rect.center,
        29
    )

    pygame.draw.circle(
        surface,
        button_color,
        exit_button_rect.center,
        25
    )

    pygame.draw.circle(
        surface,
        GOLD_DARK,
        exit_button_rect.center,
        27,
        width=2
    )

    # --------------------------------------------------------
    # Красный крестик
    # --------------------------------------------------------

    cx, cy = exit_button_rect.center

    pygame.draw.line(
        surface,
        IVORY,
        (cx - 12, cy - 12),
        (cx + 12, cy + 12),
        5
    )

    pygame.draw.line(
        surface,
        IVORY,
        (cx + 12, cy - 12),
        (cx - 12, cy + 12),
        5
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

    # --------------------------------------------------------
    # Настройки имён игроков
    # --------------------------------------------------------

    player_font_name = "Georgia"
    player_font_size = 44
    player_font_bold = True

    player_positions = [
        (WIDTH // 2 - 55, HEIGHT - 28),
        (133, 23),
        (WIDTH - 135, 23),
    ]

    # --------------------------------------------------------
    # Настройки количества взяток
    # --------------------------------------------------------

    tricks_font_name = "Georgia"
    tricks_font_size = 44
    tricks_font_bold = True

    tricks_positions = [
        None,
        (440, 23),
        (WIDTH - 440, 23),
    ]

    # --------------------------------------------------------
    # Шрифты
    # --------------------------------------------------------

    player_font = pygame.font.SysFont(
        player_font_name,
        player_font_size,
        bold=player_font_bold
    )

    tricks_font = pygame.font.SysFont(
        tricks_font_name,
        tricks_font_size,
        bold=tricks_font_bold
    )

    names = [
        "вы —",
        "СТУДЕНТ",
        "ДОЦЕНТ"
    ]

    # --------------------------------------------------------
    # Отрисовка
    # --------------------------------------------------------

    for index, (x, y) in enumerate(player_positions):

        name = names[index]

        label = player_font.render(
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
                center=tricks_positions[index]
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

    if (
        game_phase in ("whist", "whist_done", "play")
        and declarer == 0
    ):

        text = declarer_contract

    elif (
        game_phase in ("whist", "whist_done", "play")
        and declarer is not None
        and declarer != 0
        and whist_actions[
            (0 - declarer - 1) % 3
        ]
    ):

        text = whist_actions[
            (0 - declarer - 1) % 3
        ]

    else:

        text = player_bids[0]

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
                background_rect.centery
            )
        )

        surface.blit(
            image,
            image_rect
        )

        x += image.get_width()

def draw_opponent_actions(surface):

    # ----------------------------------------------------
    # Определяем, какие решения вистующих показывать
    # ----------------------------------------------------

    if (
        declarer is not None
        and (
            game_phase in (
                "whist",
                "whist_done",
                "play",
                "result"
            )
            or whist_actions[0]
            or whist_actions[1]
        )
    ):

        whist_display_actions = {
            (declarer + 1) % 3: whist_actions[0],
            (declarer + 2) % 3: whist_actions[1]
        }

    else:

        whist_display_actions = {}

    # ----------------------------------------------------
    # Шрифты
    # ----------------------------------------------------

    font = pygame.font.SysFont(
        "Georgia",
        64
    )

    suit_font = pygame.font.SysFont(
        "DejaVu Sans",
        86
    )

    # ----------------------------------------------------
    # Функция отрисовки текста
    # ----------------------------------------------------

    def draw_action(text, x, y):

        if not text:
            return

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

        # ------------------------------------------------
        # ПОЛВИСТА — две строки
        # ------------------------------------------------

        if text == "ПОЛВИСТА":

            small_font = pygame.font.SysFont(
                "Georgia",
                50
            )

            line1 = small_font.render(
                "ПОЛ",
                True,
                BLACK
            )

            line2 = small_font.render(
                "ВИСТА",
                True,
                BLACK
            )

            # Центрируем каждую строку
            line1_x = (
                background_rect.centerx
                - line1.get_width() // 2
            )

            line2_x = (
                background_rect.centerx
                - line2.get_width() // 2
            )

            surface.blit(
                line1,
                (
                    line1_x,
                    y - 12
                )
            )

            surface.blit(
                line2,
                (
                    line2_x,
                    y + 42
                )
            )

            return

        # ------------------------------------------------
        # Обычные надписи
        # ------------------------------------------------

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
    # Левый соперник
    # ----------------------------------------------------

    if (
        declarer is not None
        and declarer == 1
        and declarer_contract
    ):

        text = declarer_contract

    elif whist_display_actions:

        text = whist_display_actions.get(
            1,
            ""
        )

    else:

        text = opponent_actions[0]

    draw_action(
        text,
        185,
        110
    )

    # ----------------------------------------------------
    # Правый соперник
    # ----------------------------------------------------

    if (
        declarer is not None
        and declarer == 2
        and declarer_contract
    ):

        text = declarer_contract

    elif whist_display_actions:

        text = whist_display_actions.get(
            2,
            ""
        )

    else:

        text = opponent_actions[1]

    draw_action(
        text,
        WIDTH - 375,
        110
    )


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
    left_y = HEIGHT // 2 - 240

    for index in range(len(player_hands[1])):

        rect = pygame.Rect(
            left_x - index * 14,
            left_y + index * 18.5,
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
    right_y = HEIGHT // 2 - 240

    for index in range(len(player_hands[2])):

        rect = pygame.Rect(
            right_x + index * 14,
            right_y + index * 18.5,
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
    suit_counts = {
        "♠": 0,
        "♣": 0,
        "♦": 0,
        "♥": 0
    }

    # --------------------------------------------------------
    # Считаем карты по мастям
    # --------------------------------------------------------

    for rank, suit in hand:

        suit_counts[suit] += 1

        if suit == trump:

            trump_cards.append(rank)

    # --------------------------------------------------------
    # Сила козырей
    # --------------------------------------------------------

    for rank in trump_cards:

        value = card_strength(rank)

        score += value * 2.0

        if rank == "Т":

            score += 7

        elif rank == "К":

            score += 4

        elif rank == "Д":

            score += 2

    # --------------------------------------------------------
    # Длина козырной масти
    #
    # Длинная козырная масть очень важна после прикупа.
    # Пять козырей должны заметно превосходить
    # три старшие карты одной масти.
    # --------------------------------------------------------

    trump_length = len(trump_cards)

    if trump_length >= 6:

        score += 18

    elif trump_length == 5:

        score += 13

    elif trump_length == 4:

        score += 7

    elif trump_length == 3:

        score += 0

    elif trump_length == 2:

        score -= 7

    # --------------------------------------------------------
    # Старшие карты в боковых мастях
    # --------------------------------------------------------

    for rank, suit in hand:

        if suit == trump:

            continue

        if rank == "Т":

            score += 5

        elif rank == "К":

            score += 2

        elif rank == "Д":

            score += 0.5

    # --------------------------------------------------------
    # Длина боковых мастей
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
    # Дополнительный бонус за очень сильный козырь.
    #
    # Туз + король в козыре особенно хороши.
    # --------------------------------------------------------

    if "Т" in trump_cards:

        score += 3

    if (
        "Т" in trump_cards
        and "К" in trump_cards
    ):

        score += 4

    # --------------------------------------------------------
    # Требуемая сила для разных уровней.
    #
    # Шкала специально сделана плавнее.
    # --------------------------------------------------------

    required = {
        6: 24,
        7: 30,
        8: 36,
        9: 42,
        10: 48
    }

    target = required.get(
        level,
        48
    )

    # --------------------------------------------------------
    # Запас силы относительно контракта.
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

def estimate_raspas_danger(hand):

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
            score += 10

        elif rank == "К":
            score += 6

        elif rank == "Д":
            score += 3

        elif rank == "В":
            score += 1

        elif rank == "10":
            score += 0.5

    for suit in suit_counts:

        count = suit_counts[suit]

        if count >= 5:
            score += 6

        elif count == 4:
            score += 4

        elif count == 3:
            score += 2

    return score


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

    print(
        "ТОРГОВЛЯ ИИ:",
        player,
        "| доступные заявки:",
        available_bids
    )

    if len(available_bids) == 1:

        return "Пас", None

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

        return "Пас", None

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

        confidence = estimate_bid_confidence(
            hand,
            bid
        )

        print(
            bid,
            "успех:",
            round(probability * 100, 1),
            "%",
            "средние взятки:",
            round(average_tricks, 2),
            "| confidence:",
            round(confidence, 1)
        )

    # --------------------------------------------------------
    # Проверяем, была ли у ИИ собственная заявка,
    # которую соперник только что перебил.
    # --------------------------------------------------------

    previous_bid = None

    for history_player, history_bid in reversed(history):

        if history_player == player:

            if history_bid != "Пас":

                previous_bid = history_bid

            break

    # --------------------------------------------------------
    # Получаем СОХРАНЁННУЮ вероятность предыдущей заявки.
    #
    # Повторно её не рассчитываем.
    # --------------------------------------------------------

    previous_probability = None

    if previous_bid is not None:

        previous_probability = (
            bot_previous_probability[player]
        )

        print(
            "ИИ:",
            player,
            "| предыдущая заявка:",
            previous_bid,
            "| сохранённый успех:",
            round(previous_probability * 100, 1)
            if previous_probability is not None
            else "нет данных"
        )

    # --------------------------------------------------------
    # Проверяем, была ли предыдущая заявка достаточно сильной.
    # --------------------------------------------------------

    defend_previous_bid = (
        previous_probability is not None
        and previous_probability >= 0.50
    )

    print(
        "ТОРГОВЛЯ ИИ:",
        player,
        "| previous_bid:",
        previous_bid,
        "| previous_probability:",
        previous_probability,
        "| defend_previous_bid:",
        defend_previous_bid
    )

    # --------------------------------------------------------
    # Выбираем заявку.
    #
    # В обычной ситуации вероятность должна быть
    # не меньше 45%.
    #
    # Но если рука объективно достаточно сильная
    # для данной заявки, ИИ может рискнуть даже
    # при низком результате симуляции.
    #
    # Это делает торговлю более похожей на игру человека:
    # сильная рука не должна автоматически превращаться
    # в "Пас" только из-за неудачной случайной симуляции.
    # --------------------------------------------------------

    if defend_previous_bid:

        reasonable = [
            item
            for item in evaluations
            if (
                item[1] >= 0.20
                if item[0] != "Мизер"
                else item[1] >= 0.50
            )
        ]

    else:

        reasonable = []

        for item in evaluations:

            bid = item[0]
            probability = item[1]

            # ------------------------------------------------
            # Мизер оставляем по старому правилу.
            # ------------------------------------------------

            if bid == "Мизер":

                if probability >= 0.50:

                    reasonable.append(item)

                continue

            # ------------------------------------------------
            # Обычное прохождение заявки по симуляции.
            # ------------------------------------------------

            if probability >= 0.45:

                reasonable.append(item)

                continue

            # ------------------------------------------------
            # Если симуляция пессимистична, проверяем
            # реальную силу руки.
            # ------------------------------------------------

            confidence = estimate_bid_confidence(
                hand,
                bid
            )

            # ------------------------------------------------
            # Сильная рука может рискнуть.
            #
            # confidence >= 15:
            # заявка достаточно сильная,
            # поэтому допускаем вероятность от 20%.
            #
            # confidence >= 25:
            # рука настолько сильная, что результат
            # симуляции уже не является обязательным
            # условием.
            # ------------------------------------------------

            if (
                probability < 0.10
            ):

                if (
                    confidence >= 40
                    and probability > 0
                ):

                    reasonable.append(item)

                    continue

            elif (
                confidence >= 25
                and probability >= 0.20
            ):

                reasonable.append(item)

                continue

            if (
                confidence >= 15
                and probability >= 0.30
            ):

                reasonable.append(item)

                continue

    print(
        "ТОРГОВЛЯ ИИ:",
        player,
        "| reasonable:",
        [
            item[0]
            for item in reasonable
        ]
    )

    if not reasonable:

        return "Пас", None

    # --------------------------------------------------------
    # Из достаточно подходящих заявок выбираем
    # самую высокую по торговле.
    # --------------------------------------------------------

    reasonable.sort(
        key=lambda item: get_bid_value(item[0])
    )

    selected_bid = reasonable[-1]

    print(
        "ТОРГОВЛЯ ИИ:",
        player,
        "| selected_bid:",
        selected_bid[0],
        "| probability:",
        round(selected_bid[1] * 100, 1),
        "%"
    )

    return (
        selected_bid[0],
        selected_bid[1]
    )

def bot_ai_worker(
    player,
    hand,
    available_bids,
    history
):

    global bot_result
    global bot_result_player
    global bot_result_probability

    # --------------------------------------------------------
    # ИИ работает только с копией руки.
    #
    # Pygame и состояние игры здесь не используются.
    # --------------------------------------------------------

    result, probability = choose_bot_bid(
        player,
        available_bids,
        history
    )

    bot_result = result
    bot_result_probability = probability
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
    global bot_result_probability
    global bot_previous_probability

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
        probability = bot_result_probability

        bot_result = None
        bot_result_probability = None
        bot_result_player = None
        bot_thinking = False

        # ----------------------------------------------------
        # Запоминаем заявку.
        # ----------------------------------------------------

        player_bids[player] = bid
        
        if bid != "Пас":

            bot_previous_probability[player] = probability

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

    print(
        "ОТЛАДКА ПРИКУП:",
        "| highest_bid:", highest_bid,
        "| player_bids:", player_bids,
        "| declarer:", declarer
    )

    if declarer is None:
        return

    declarer_contract = highest_bid

    game_phase = "talon"

def start_raspasovka():

    global game_phase
    global declarer
    global declarer_contract
    global play_current_player
    global trick_cards
    global trick_lead_suit
    global trick_winner
    global trick_number
    global played_cards
    global trick_pause
    global trick_pause_start
    global raspasovka

    raspasovka = True

    declarer = None
    declarer_contract = "Распасовка"

    play_current_player = (
        dealer + 1
    ) % 3

    trick_cards = []
    played_cards = []

    trick_lead_suit = None
    trick_winner = None

    trick_number = 1

    trick_pause = False
    trick_pause_start = 0

    game_phase = "play"

    print(
        "РАСПАСОВКА: начало",
        "| сдающий:",
        dealer,
        "| первый ход:",
        play_current_player
    )


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

            start_raspasovka()

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
    global trick_pause
    global trick_pause_start

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

def determine_trick_winner():

    if not trick_cards:
        return None

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

    # --------------------------------------------------------
    # Определяем козырь
    # --------------------------------------------------------

    trump_suit = None

    if declarer_contract not in (
        "",
        "Мизер",
        "Распасовка"
    ):

        if not declarer_contract.endswith("БК"):
            trump_suit = declarer_contract[-1]

    # --------------------------------------------------------
    # Первый игрок пока считается победителем
    # --------------------------------------------------------

    winner_player, winner_card = trick_cards[0]

    # --------------------------------------------------------
    # Проверяем остальные карты
    # --------------------------------------------------------

    for player, card in trick_cards[1:]:

        # ----------------------------------------------------
        # Если текущая карта — козырь
        # ----------------------------------------------------

        if trump_suit is not None:

            if card[1] == trump_suit:

                # Если победитель ещё не козырь —
                # новый козырь автоматически сильнее.
                if winner_card[1] != trump_suit:

                    winner_player = player
                    winner_card = card
                    continue

                # Если оба козырные —
                # сравниваем их достоинство.
                if (
                    rank_order[card[0]]
                    > rank_order[winner_card[0]]
                ):

                    winner_player = player
                    winner_card = card

                continue

            # ------------------------------------------------
            # Текущая карта не козырь,
            # а победитель уже козырный.
            # ------------------------------------------------

            if winner_card[1] == trump_suit:
                continue

        # ----------------------------------------------------
        # Карта не козырь.
        # Она может выиграть только если
        # относится к масти хода.
        # ----------------------------------------------------

        if card[1] != trick_lead_suit:
            continue

        # ----------------------------------------------------
        # Если победитель пока был другой масти,
        # карта масти хода становится победителем.
        # ----------------------------------------------------

        if winner_card[1] != trick_lead_suit:

            winner_player = player
            winner_card = card
            continue

        # ----------------------------------------------------
        # Обе карты масти хода —
        # сравниваем достоинство.
        # ----------------------------------------------------

        if (
            rank_order[card[0]]
            > rank_order[winner_card[0]]
        ):

            winner_player = player
            winner_card = card

    return winner_player

def bot_make_play():

    global play_current_player
    global trick_cards
    global played_cards
    global trick_lead_suit
    global trick_winner
    global trick_pause
    global trick_pause_start

    if game_phase != "play":
        return

    if play_current_player == 0:
        return

    player = play_current_player

    if not player_hands[player]:
        return

    # --------------------------------------------------------
    # Определяем козырь
    # --------------------------------------------------------

    if raspasovka:

        suit = "Распасовка"
        level = 0
        trump = None

    else:

        suit, level = get_bid_contract(
            declarer_contract
        )

        if suit in ("БК", "Мизер"):
            trump = None
        else:
            trump = suit

    # --------------------------------------------------------
    # Определяем роль игрока
    # --------------------------------------------------------

    if raspasovka:

        role = "pass"
        action = ""

    elif player == declarer:

        role = "declarer"
        action = ""

    else:

        action_index = (
            player
            - declarer
            - 1
        ) % 3

        action = whist_actions[
            action_index
        ]

        if action == "ВИСТ":
            role = "whist"

        elif action == "ПОЛВИСТА":
            role = "half_whist"

        else:
            role = "pass"

    # --------------------------------------------------------
    # Стратегическая цель по взяткам
    #
    # NEED_TRICKS  - взяток пока не хватает
    # SAFE         - необходимая норма уже выполнена
    # AVOID_TRICKS - нужно избегать взяток
    # --------------------------------------------------------

    goal_state = "AVOID_TRICKS"

    required_tricks = 0

    # --------------------------------------------------------
    # Мизер
    # --------------------------------------------------------

    if suit == "Мизер":

        if player == declarer:

            # Разыгрывающий старается
            # вообще не брать взятки.
            goal_state = "AVOID_TRICKS"

        elif role == "pass":

            # Пасующий на Мизере также старается
            # избегать взяток.
            goal_state = "AVOID_TRICKS"

        else:

            # Вистующий / полвистующий старается
            # брать взятки и мешать разыгрывающему.
            goal_state = "NEED_TRICKS"

    # --------------------------------------------------------
    # Обычный контракт
    # --------------------------------------------------------

    else:

        if role == "declarer":

            required_tricks = level

            if tricks_won[player] < required_tricks:

                goal_state = "NEED_TRICKS"

            else:

                # Контракт уже выполнен.
                # Теперь не нужно бездумно брать новые взятки.
                goal_state = "SAFE"

        elif role == "pass":

            # Пасующий всё равно играет карты,
            # но старается не брать взятки.
            goal_state = "AVOID_TRICKS"

        elif role == "whist":

            required_tricks = {
                6: 4,
                7: 2,
                8: 1,
                9: 1,
                10: 1
            }.get(
                level,
                1
            )

            if tricks_won[player] < required_tricks:

                # Вистующим пока нужны взятки.
                goal_state = "NEED_TRICKS"

            else:

                # Норма уже выполнена.
                # Теперь стараемся не брать лишнего.
                goal_state = "SAFE"

        elif role == "half_whist":

            required_tricks = {
                6: 2,
                7: 1
            }.get(
                level,
                1
            )

            if tricks_won[player] < required_tricks:

                goal_state = "NEED_TRICKS"

            else:

                goal_state = "SAFE"

    # --------------------------------------------------------
    # Для отладки
    # --------------------------------------------------------

    print(
        "РОЗЫГРЫШ: цель ИИ",
        player,
        "| состояние:",
        goal_state,
        "| взятки:",
        tricks_won[player],
        "| норма:",
        required_tricks
    )

    # --------------------------------------------------------
    # Определяем разрешённые карты
    # --------------------------------------------------------

    hand = player_hands[player]

    if trick_cards:

        same_suit_cards = [
            card
            for card in hand
            if card[1] == trick_lead_suit
        ]

        if same_suit_cards:

            legal_cards = same_suit_cards

        elif trump is not None:

            trump_cards = [
                card
                for card in hand
                if card[1] == trump
            ]

            if trump_cards:

                legal_cards = trump_cards

            else:

                legal_cards = hand

        else:

            legal_cards = hand

    else:

        legal_cards = hand

    # --------------------------------------------------------
    # Определяем, берёт ли карта текущую взятку
    # --------------------------------------------------------

    def card_wins(card):

        trick_cards.append(
            (player, card)
        )

        winner = determine_trick_winner()

        trick_cards.pop()

        return winner == player

    # --------------------------------------------------------
    # Насколько карта сильная
    # --------------------------------------------------------

    def card_value(card):

        return card_strength(
            card[0]
        )

    # --------------------------------------------------------
    # Оценка будущей руки
    #
    # Здесь бот смотрит:
    # - какие сильные карты останутся;
    # - сколько козырей останется;
    # - есть ли короткие масти;
    # - сколько вообще карт останется.
    #
    # Это не полный просчёт сдачи, а небольшой
    # человеческий взгляд вперёд.
    # --------------------------------------------------------

    def future_value(card):

        remaining_hand = [
            c
            for c in hand
            if c != card
        ]

        if not remaining_hand:
            return 0

        value = 0

        # ----------------------------------------------------
        # Сохраняем сильные карты
        # ----------------------------------------------------

        for remaining_card in remaining_hand:

            strength = card_value(
                remaining_card
            )

            if strength >= 6:
                value += 2

            if strength >= 7:
                value += 2

        # ----------------------------------------------------
        # Козыри особенно ценны
        # ----------------------------------------------------

        if trump is not None:

            remaining_trumps = [
                c
                for c in remaining_hand
                if c[1] == trump
            ]

            value += (
                len(remaining_trumps) * 3
            )

            # Старший козырь особенно ценен.
            for c in remaining_trumps:

                if card_value(c) >= 6:
                    value += 2

        # ----------------------------------------------------
        # Короткая масть даёт возможность
        # избавиться от неё позже.
        # ----------------------------------------------------

        suits = (
            "♠",
            "♣",
            "♦",
            "♥"
        )

        for current_suit in suits:

            count = sum(
                1
                for c in remaining_hand
                if c[1] == current_suit
            )

            if count == 1:
                value += 2

            elif count == 0:
                value += 3

        return value

    # --------------------------------------------------------
    # Оценка конкретной карты
    #
    # Чем выше score, тем предпочтительнее карта.
    # --------------------------------------------------------

    def evaluate_card(card):

        wins_now = False
        simulated_winner = None

        if trick_cards:

            wins_now = card_wins(
                card
            )

            # ------------------------------------------------
            # Временно добавляем карту во взятку
            # и определяем, кому она достанется.
            # ------------------------------------------------

            trick_cards.append(
                (player, card)
            )

            simulated_winner = (
                determine_trick_winner()
            )

            trick_cards.pop()

        score = 0

        current_strength = card_value(
            card
        )

        future = future_value(
            card
        )

        # ----------------------------------------------------
        # Оцениваем, кому достанется взятка
        # и кто после неё будет ходить первым.
        #
        # Победитель текущей взятки автоматически
        # становится первым ходящим в следующей.
        # ----------------------------------------------------

        if simulated_winner is not None:

            if goal_state == "NEED_TRICKS":

                if simulated_winner == player:

                    # Для ИИ, которому нужны взятки,
                    # собственный следующий ход полезен.
                    score += 18

                elif simulated_winner == declarer:

                    # Декларант будет вести следующую взятку.
                    score -= 12

                else:

                    # Другой защитник будет вести.
                    score += 8

            elif goal_state == "SAFE":

                if simulated_winner == player:

                    # Норма уже выполнена.
                    # Лучше не получать право следующего хода.
                    score -= 18

                elif simulated_winner == declarer:

                    # Декларант будет вести следующую взятку.
                    score += 12

                else:

                    # Другой защитник будет вести.
                    score += 6

            elif goal_state == "AVOID_TRICKS":

                if simulated_winner == player:

                    # ПАС сам будет начинать следующую взятку.
                    score -= 22

                elif simulated_winner == declarer:

                    # Декларант будет начинать следующую взятку.
                    score += 14

                else:

                    # Другой защитник будет начинать.
                    score += 7

        # ----------------------------------------------------
        # Если ПАС или SAFE вынужден начинать следующую
        # взятку, оцениваем качество выхода.
        #
        # Нам особенно важны:
        # 1. слабая карта;
        # 2. короткая масть;
        # 3. возможность быстро избавиться от масти;
        # 4. вероятность, что следующий игрок сможет
        #    перебить выход.
        # ----------------------------------------------------

        if (
            simulated_winner == player
            and goal_state in ("AVOID_TRICKS", "SAFE")
        ):

            exit_suit_count = sum(
                1
                for c in hand
                if c[1] == card[1]
            )

            # Слабый выход безопаснее сильного.
            score += (
                35
                - current_strength * 4
            )

            # Короткая масть особенно интересна.
            if exit_suit_count == 1:

                score += 18

            elif exit_suit_count == 2:

                score += 8

            # Очень сильная карта нежелательна.
            if current_strength >= 6:

                score -= 12

            # ------------------------------------------------
            # Оцениваем вероятность того, что выход
            # будет перебит следующим игроком.
            #
            # Чужие руки НЕ смотрим.
            # ------------------------------------------------

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

            suits = [
                "♠",
                "♣",
                "♦",
                "♥"
            ]

            ranks = [
                "7",
                "8",
                "9",
                "10",
                "В",
                "Д",
                "К",
                "Т"
            ]

            known_cards = set(
                hand
            )

            for _, played_card in played_cards:

                known_cards.add(
                    played_card
                )

            known_cards.add(
                card
            )

            unknown_cards = []

            for suit_name in suits:

                for rank_name in ranks:

                    unknown_card = (
                        rank_name,
                        suit_name
                    )

                    if unknown_card not in known_cards:

                        unknown_cards.append(
                            unknown_card
                        )

            # ------------------------------------------------
            # Оцениваем вероятность, что наш выход
            # заберёт первый или третий игрок.
            #
            # Чужие реальные руки НЕ смотрим.
            # Используем только неизвестные карты.
            # ------------------------------------------------

            next_player_can_win = 0

            for unknown_card in unknown_cards:

                can_win = False

                # Старшая карта нашей масти.
                if unknown_card[1] == card[1]:

                    if (
                        rank_order[
                            unknown_card[0]
                        ]
                        >
                        rank_order[
                            card[0]
                        ]
                    ):

                        can_win = True

                # Козырь может перебить выход.
                elif (
                    trump is not None
                    and unknown_card[1] == trump
                    and card[1] != trump
                ):

                    can_win = True

                if can_win:

                    next_player_can_win += 1

            if len(unknown_cards) > 0:

                next_probability = (
                    next_player_can_win
                    / len(unknown_cards)
                )

            else:

                next_probability = 0

            # ------------------------------------------------
            # Теперь учитываем третьего игрока.
            #
            # Если первая неизвестная карта НЕ может
            # перебить наш выход, вторая неизвестная карта
            # получает такую возможность.
            # ------------------------------------------------

            third_player_can_win = 0

            third_player_total = 0

            for first_card in unknown_cards:

                first_can_win = False

                if first_card[1] == card[1]:

                    if (
                        rank_order[
                            first_card[0]
                        ]
                        >
                        rank_order[
                            card[0]
                        ]
                    ):

                        first_can_win = True

                elif (
                    trump is not None
                    and first_card[1] == trump
                    and card[1] != trump
                ):

                    first_can_win = True

                # Первый игрок уже забирает взятку.
                # До третьего игрока дело не доходит.
                if first_can_win:

                    continue

                for second_card in unknown_cards:

                    if second_card == first_card:
                        continue

                    third_player_total += 1

                    second_can_win = False

                    if second_card[1] == card[1]:

                        if (
                            rank_order[
                                second_card[0]
                            ]
                            >
                            rank_order[
                                card[0]
                            ]
                        ):

                            second_can_win = True

                    elif (
                        trump is not None
                        and second_card[1] == trump
                        and card[1] != trump
                    ):

                        second_can_win = True

                    if second_can_win:

                        third_player_can_win += 1

            if third_player_total > 0:

                third_probability = (
                    third_player_can_win
                    / third_player_total
                )

            else:

                third_probability = 0

            # ------------------------------------------------
            # Общая вероятность избавиться от взятки:
            #
            # первый игрок перебивает
            # ИЛИ
            # первый не перебивает, но перебивает третий.
            # ------------------------------------------------

            escape_probability = (
                next_probability
                + (
                    (1 - next_probability)
                    * third_probability
                )
            )

            # ------------------------------------------------
            # Для ПАСА особенно выгоден выход,
            # который с большой вероятностью заберёт
            # другой игрок.
            # ------------------------------------------------

            if goal_state == "AVOID_TRICKS":

                score += int(
                    escape_probability * 80
                )

            elif goal_state == "SAFE":

                score += int(
                    escape_probability * 55
                )

            # ------------------------------------------------
            # Если выход почти наверняка останется
            # у самого ИИ, это плохой выход.
            # ------------------------------------------------

            if escape_probability < 0.20:

                if goal_state == "AVOID_TRICKS":

                    score -= 30

                elif goal_state == "SAFE":

                    score -= 20

        # ----------------------------------------------------
        # Взятки нужны
        # ----------------------------------------------------

        if goal_state == "NEED_TRICKS":

            if (
                player == declarer
                and not trick_cards
                and trump is not None
                and card[1] != trump
            ):

                score -= 20

            if (
                player == declarer
                and not trick_cards
                and trump is not None
            ):

                suit, level = get_bid_contract(
                    declarer_contract
                )

                tricks_needed = (
                    level
                    - tricks_won[declarer]
                )

                cards_remaining = len(hand)

                if (
                    cards_remaining > 0
                    and tricks_needed >= 2
                    and (
                        tricks_needed
                        / cards_remaining
                    ) >= 0.50
                    and card[1] == trump
                ):

                    score += 15

            if wins_now:

                # Взятка сейчас полезна.
                score += 100

                # ------------------------------------------------
                # Если декларанту осталось получить почти все
                # оставшиеся взятки, текущая взятка становится
                # особенно важной.
                #
                # Например:
                # контракт 6
                # уже взято 3
                # осталось 4 карты
                # нужно ещё 3 взятки.
                #
                # Здесь нельзя относиться к текущей взятке
                # так же, как в ситуации "нужна только 1 из 4".
                # ------------------------------------------------

                suit, level = get_bid_contract(
                    declarer_contract
                )

                if suit == "Мизер":

                    # Для вистующего на Мизере
                    # нет контрактной нормы уровня 6-10.
                    # Поэтому расчёт срочности контракта
                    # здесь не применяем.
                    tricks_needed = 0

                else:

                    tricks_needed = (
                        level
                        - tricks_won[declarer]
                    )

                cards_remaining = len(hand)

                if (
                    cards_remaining > 0
                    and (
                        tricks_needed
                        / cards_remaining
                    ) >= 0.80
                ):

                    score += 50

                elif (
                    cards_remaining > 0
                    and (
                        tricks_needed
                        / cards_remaining
                    ) >= 0.66
                ):

                    score += 40

                elif (
                    cards_remaining > 0
                    and (
                        tricks_needed
                        / cards_remaining
                    ) >= 0.50
                ):

                    score += 25

                print(
                    "ПЛАН ВЗЯТОК:",
                    card,
                    "| взято:",
                    tricks_won[declarer],
                    "| нужно:",
                    tricks_needed,
                    "| карт осталось:",
                    cards_remaining,
                    "| дефицит:",
                    tricks_needed - cards_remaining,
                    "| future:",
                    future,
                    "| score после срочности:",
                    score
                )

                # Но берём её по возможности
                # минимальной картой.
                score -= (
                    current_strength * 4
                )

                # ------------------------------------------------
                # Если это козырь и он уже гарантированно
                # выигрывает текущую взятку, стараемся
                # сохранить более старший козырь на потом.
                #
                # Например:
                # 9♥ и Т♥ обе берут взятку.
                # Если сыграть 9♥, Т♥ останется для следующей.
                # ------------------------------------------------

                if (
                    trump is not None
                    and card[1] == trump
                ):

                    stronger_trump_remaining = False

                    for other_card in hand:

                        if other_card == card:
                            continue

                        if (
                            other_card[1] == trump
                            and card_value(other_card)
                            > current_strength
                        ):

                            stronger_trump_remaining = True
                            break

                    if stronger_trump_remaining:

                        score += 20

            else:

                # Если взять сейчас нельзя,
                # смотрим, кому уйдёт взятка.

                if player == declarer:

                    # ------------------------------------------------
                    # Декларанту сейчас особенно важно
                    # не отдавать взятку сопернику.
                    #
                    # Если текущую взятку получает не декларант,
                    # это прямой минус для выполнения контракта.
                    # ------------------------------------------------

                    if (
                        simulated_winner is not None
                        and simulated_winner != declarer
                    ):

                        score -= 40

                    elif simulated_winner == declarer:

                        # Карта всё-таки приводит к нашей взятке.
                        score += 15

                else:

                    # ------------------------------------------------
                    # Для ВИСТА оставляем прежнюю логику.
                    # ------------------------------------------------

                    if simulated_winner == declarer:

                        # ВИСТУ невыгодно просто отдавать
                        # взятку разыгрывающему.
                        score -= 55

                    elif (
                        simulated_winner is not None
                        and simulated_winner != player
                    ):

                        # Другой противник получил взятку.
                        score += 20

                # При невозможности взять
                # лучше не выбрасывать сильную карту.
                score -= (
                    current_strength * 2
                )

        # ----------------------------------------------------
        # Норма уже выполнена
        # ----------------------------------------------------

        elif goal_state == "SAFE":

            if wins_now:

                # Лишнюю взятку брать не хочется.
                score -= 100

                # Сильную карту особенно жалко тратить.
                score -= (
                    current_strength * 3
                )

                score += (
                    future * 2
                )

            else:

                # Теперь важно, кому достанется взятка.
                if simulated_winner == declarer:

                    # Отдать взятку декларанту
                    # после выполнения своей нормы нежелательно.
                    score -= 35

                elif (
                    simulated_winner is not None
                    and simulated_winner != player
                ):

                    # Взятка достанется другому противнику.
                    score += 15

                score += 60

                score -= (
                    current_strength * 2
                )

        # ----------------------------------------------------
        # Взятки нужно избегать
        # ----------------------------------------------------

        elif goal_state == "AVOID_TRICKS":

            # Чем больше взяток уже набрал ИИ,
            # тем сильнее он старается не получать следующую.
            current_tricks = tricks_won[player]

            # ------------------------------------------------
            # Базовый штраф за собственную взятку.
            #
            # Важен не только сам факт взятки,
            # но и её место в уже набранном количестве.
            # ------------------------------------------------

            if simulated_winner == player:

                score -= (
                    120
                    + current_tricks * 35
                )

                if current_tricks >= 1:

                    score -= (
                        current_tricks
                        * (current_tricks + 3)
                        * 5
                    )

            # ------------------------------------------------
            # Если взятку получает другой игрок,
            # оцениваем распределение взяток.
            # ------------------------------------------------

            elif (
                simulated_winner is not None
                and simulated_winner != player
            ):

                winner_tricks = (
                    tricks_won[simulated_winner]
                )

                trick_difference = (
                    winner_tricks
                    - current_tricks
                )

                # Другой игрок уже имеет больше взяток.
                # Отдать ему следующую обычно разумно:
                # распределение становится ближе к равному.
                if trick_difference > 0:

                    score += min(
                        trick_difference * 14,
                        42
                    )

                # Равное количество взяток —
                # хороший вариант распределения.
                elif trick_difference == 0:

                    score += 24

                # Другой игрок отстаёт.
                # Помогать ему набирать ещё взятки
                # уже нежелательно.
                else:

                    score -= min(
                        abs(trick_difference) * 14,
                        42
                    )

            # ------------------------------------------------
            # Взятка декларанту особенно нежелательна:
            # пасующий не хочет помогать разыгрывающему.
            # ------------------------------------------------

            if simulated_winner == declarer:

                score -= 45

                score -= (
                    current_tricks * 10
                )

            # ------------------------------------------------
            # Если ИИ НЕ получает текущую взятку,
            # карта в целом безопасна.
            # ------------------------------------------------

            if simulated_winner != player:

                score += 50

                score -= (
                    current_strength * 3
                )

            # ------------------------------------------------
            # ДВУХШАГОВЫЙ ПРОГНОЗ
            #
            # Если текущая карта приводит к нашей взятке,
            # следующий ход снова будет нашим.
            #
            # Поэтому смотрим на оставшиеся карты и ищем
            # наиболее безопасный следующий выход.
            # ------------------------------------------------

            if simulated_winner == player:

                best_next_escape = 0

                for next_card in hand:

                    if next_card == card:
                        continue

                    next_escape = 0

                    for unknown_card in unknown_cards:

                        next_can_win = False

                        # Карта той же масти старше
                        # нашего следующего выхода.
                        if unknown_card[1] == next_card[1]:

                            if (
                                rank_order[
                                    unknown_card[0]
                                ]
                                >
                                rank_order[
                                    next_card[0]
                                ]
                            ):

                                next_can_win = True

                        # Козырь перебивает обычную масть.
                        elif (
                            trump is not None
                            and unknown_card[1] == trump
                            and next_card[1] != trump
                        ):

                            next_can_win = True

                        if next_can_win:

                            next_escape += 1

                    if len(unknown_cards) > 0:

                        next_escape_probability = (
                            next_escape
                            / len(unknown_cards)
                        )

                    else:

                        next_escape_probability = 0

                    if (
                        next_escape_probability
                        >
                        best_next_escape
                    ):

                        best_next_escape = (
                            next_escape_probability
                        )

                # ------------------------------------------------
                # Теперь знаем, насколько реально ИИ сможет
                # избавиться от следующей взятки.
                # ------------------------------------------------

                if best_next_escape >= 0.70:

                    score += 25

                elif best_next_escape >= 0.50:

                    score += 5

                elif best_next_escape >= 0.35:

                    score -= 20

                elif best_next_escape >= 0.20:

                    score -= 45

                else:

                    score -= 70

                # ------------------------------------------------
                # После двух взяток особенно важно не получать
                # третью, если следующий выход тоже опасный.
                # ------------------------------------------------

                if current_tricks >= 2:

                    if best_next_escape < 0.50:

                        score -= 30

                # ------------------------------------------------
                # После трёх взяток цена следующей ещё выше.
                # ------------------------------------------------

                if current_tricks >= 3:

                    if best_next_escape < 0.60:

                        score -= 40

            # ------------------------------------------------
            # Если ИИ уже набрал много взяток,
            # дополнительно усиливаем желание от них уйти.
            # ------------------------------------------------

            if current_tricks >= 2:

                if simulated_winner == player:

                    score -= (
                        current_tricks * 15
                    )

                elif (
                    simulated_winner is not None
                    and simulated_winner != player
                ):

                    score += 5

            if current_tricks >= 3:

                if simulated_winner == player:

                    score -= 30

            # ------------------------------------------------
            # Если текущая карта слабая и безопасная,
            # небольшое преимущество отдаём именно ей.
            # ------------------------------------------------

            if simulated_winner != player:

                score += (
                    20
                    - current_strength * 2
                )

        # ----------------------------------------------------
        # Козырь не следует тратить без причины.
        # Но если у декларанта много козырей
        # и нужны взятки, слабый козырь может быть
        # полезным способом сохранить контроль масти.
        # ----------------------------------------------------

        if trump is not None:

            if card[1] == trump:

                if goal_state != "NEED_TRICKS":

                    score -= 15

                elif not wins_now:

                    score -= 10

                    trump_count = sum(
                        1
                        for c in hand
                        if c[1] == trump
                    )

                    if trump_count >= 5:

                        score += 12

                    elif trump_count == 4:

                        score += 6

        # ----------------------------------------------------
        # На первом ходе нет текущей взятки.
        # Поэтому отдельно оцениваем направление хода.
        # ----------------------------------------------------

        if not trick_cards:

            if goal_state == "NEED_TRICKS":

                # ВИСТ/декларант любит начинать
                # сильной картой, но не обязательно
                # самой старшей.
                score += (
                    current_strength * 5
                )

                if trump is not None:
                    if card[1] == trump:
                        score -= 8

                # ------------------------------------------------
                # Риск выхода в боковую масть.
                #
                # Сильная боковая карта может быть перебита
                # козырем противника. Мы не знаем его руку,
                # поэтому оцениваем только неизвестные карты.
                #
                # Это не запрет на такой выход, а небольшой
                # штраф за слишком опасный первый ход.
                # ------------------------------------------------

                if (
                    trump is not None
                    and card[1] != trump
                ):

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

                    suits = [
                        "♠",
                        "♣",
                        "♦",
                        "♥"
                    ]

                    ranks = [
                        "7",
                        "8",
                        "9",
                        "10",
                        "В",
                        "Д",
                        "К",
                        "Т"
                    ]

                    known_cards = set(
                        hand
                    )

                    for _, played_card in played_cards:

                        known_cards.add(
                            played_card
                        )

                    known_cards.add(
                        card
                    )

                    unknown_cards = []

                    for suit_name in suits:

                        for rank_name in ranks:

                            unknown_card = (
                                rank_name,
                                suit_name
                            )

                            if unknown_card not in known_cards:

                                unknown_cards.append(
                                    unknown_card
                                )

                    trump_cards = 0

                    for unknown_card in unknown_cards:

                        if unknown_card[1] == trump:

                            trump_cards += 1

                    if len(unknown_cards) > 0:

                        trump_probability = (
                            trump_cards
                            / len(unknown_cards)
                        )

                    else:

                        trump_probability = 0

                    # Старшая боковая карта особенно жалко
                    # отдавать под козырь.
                    if current_strength >= 7:

                        score -= int(
                            trump_probability * 18
                        )

                    elif current_strength >= 6:

                        score -= int(
                            trump_probability * 10
                        )

                    # ------------------------------------------------
                    # Риск быть перебитым старшей картой той же масти.
                    #
                    # Если у неизвестных карт есть карты старше
                    # нашей, такой выход может сразу отдать взятку.
                    # Штраф небольшой, чтобы ИИ не боялся
                    # разыгрывать боковые масти вообще.
                    # ------------------------------------------------

                    higher_same_suit = 0

                    for unknown_card in unknown_cards:

                        if (
                            unknown_card[1] == card[1]
                            and rank_order[
                                unknown_card[0]
                            ] > rank_order[
                                card[0]
                            ]
                        ):

                            higher_same_suit += 1

                    if higher_same_suit == 1:

                        score -= 4

                    elif higher_same_suit == 2:

                        score -= 8

                    elif higher_same_suit >= 3:

                        score -= 12

            else:

                # ПАС старается начинать безопасно.
                score += (
                    40
                    - current_strength * 5
                )

                # Короткая масть может быть полезна:
                # после её окончания можно будет
                # сбрасывать другие карты.
                suit_count = sum(
                    1
                    for c in hand
                    if c[1] == card[1]
                )

                if suit_count == 1:
                    score += 8

        # ----------------------------------------------------
        # Если карта оставляет после себя
        # хороший набор — это дополнительный плюс.
        # ----------------------------------------------------

        score += future

        return score

    # --------------------------------------------------------
    # Выбираем карту с учётом текущей ситуации
    # и небольшой оценки будущего.
    # --------------------------------------------------------

    print(
        "ОЦЕНКИ КАРТ ИИ",
        player,
        "| цель:",
        goal_state
    )

    best_card = legal_cards[0]
    best_score = evaluate_card(
        best_card
    )

    print(
        "   ",
        best_card,
        "->",
        round(best_score, 1)
    )

    for candidate in legal_cards[1:]:

        candidate_score = evaluate_card(
            candidate
        )

        print(
            "   ",
            candidate,
            "->",
            round(candidate_score, 1)
        )

        if candidate_score > best_score:

            best_card = candidate
            best_score = candidate_score

    card = best_card

    # --------------------------------------------------------
    # Играем карту
    # --------------------------------------------------------

    print(
        "РОЗЫГРЫШ: ИИ",
        player,
        "| роль:",
        role,
        "| решение:",
        action,
        "| взятки:",
        tricks_won[player],
        "| сыграл:",
        card
    )

    trick_cards.append(
        (player, card)
    )

    if len(trick_cards) == 1:

        trick_lead_suit = card[1]

    played_cards.append(
        (player, card)
    )

    player_hands[player].remove(
        card
    )

    # --------------------------------------------------------
    # Закончилась взятка
    # --------------------------------------------------------

    if len(trick_cards) == 3:

        trick_winner = determine_trick_winner()

        tricks_won[
            trick_winner
        ] += 1

        print(
            "РОЗЫГРЫШ: взятку взял:",
            trick_winner
        )

        trick_pause = True

        trick_pause_start = (
            pygame.time.get_ticks()
        )

        return

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

    if talon_taken:
        return

    # --------------------------------------------------------
    # Забираем обе карты прикупа в руку декларанта.
    # --------------------------------------------------------

    player_hands[declarer].extend(talon)

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

    player_hands[declarer].sort(
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

def bot_make_discard():

    global game_phase
    global player_hands
    global discard_selection
    global whist_current_player
    global whist_actions

    if game_phase != "discard":
        return

    if declarer == 0:
        return

    if declarer is None:
        return

    hand = player_hands[declarer]

    if len(hand) != 12:
        return

    # --------------------------------------------------------
    # Определяем контракт и козырь.
    # --------------------------------------------------------

    suit, level = get_bid_contract(
        declarer_contract
    )

    trump = None

    if suit not in ("БК", "Мизер"):
        trump = suit

    # --------------------------------------------------------
    # Количество карт каждой масти.
    # --------------------------------------------------------

    suit_counts = {
        "♠": 0,
        "♣": 0,
        "♦": 0,
        "♥": 0
    }

    for card in hand:
        suit_counts[card[1]] += 1

    # --------------------------------------------------------
    # Оцениваем карту именно с точки зрения сноса.
    #
    # Чем выше score —
    # тем больше карта подходит для сноса.
    # --------------------------------------------------------

    discard_scores = []

    for card in hand:

        rank = card[0]
        card_suit = card[1]

        strength = card_strength(rank)

        score = 0

        # ----------------------------------------------------
        # Мизер.
        #
        # Здесь сильные карты опасны,
        # поэтому их наоборот хочется убрать.
        # ----------------------------------------------------

        if suit == "Мизер":

            score += strength * 12

            if rank == "Т":
                score += 20

            elif rank == "К":
                score += 14

            elif rank == "Д":
                score += 8

            # Одиночная сильная карта особенно неудобна.
            if suit_counts[card_suit] == 1:
                score += 8

        # ----------------------------------------------------
        # Обычный контракт с козырем.
        # ----------------------------------------------------

        elif trump is not None:

            # Козыри стараемся сохранять.
            if card_suit == trump:

                score -= 40

                if rank == "Т":
                    score -= 25

                elif rank == "К":
                    score -= 18

                elif rank == "Д":
                    score -= 10

            else:

                # Слабые боковые карты —
                # основные кандидаты на снос.
                score += (
                    28
                    - strength * 5
                )

                # Одиночная боковая масть может быть
                # очень полезна для последующего
                # сокращения масти.
                if suit_counts[card_suit] == 1:

                    score += 10

                # Старшие карты сохраняем.
                if rank == "Т":
                    score -= 20

                elif rank == "К":
                    score -= 12

                elif rank == "Д":
                    score -= 6

        # ----------------------------------------------------
        # Бескозырка.
        # ----------------------------------------------------

        else:

            score += (
                28
                - strength * 5
            )

            if rank == "Т":
                score -= 20

            elif rank == "К":
                score -= 12

            elif rank == "Д":
                score -= 6

            if suit_counts[card_suit] == 1:
                score += 6

        discard_scores.append(
            (score, card)
        )

    # --------------------------------------------------------
    # Сортируем от наиболее подходящей для сноса
    # карты к наименее подходящей.
    # --------------------------------------------------------

    discard_scores.sort(
        key=lambda item: item[0],
        reverse=True
    )

    selected_cards = [
        discard_scores[0][1],
        discard_scores[1][1]
    ]

    # --------------------------------------------------------
    # Находим индексы этих карт в текущей руке.
    # --------------------------------------------------------

    discard_selection = []

    for index, card in enumerate(hand):

        if card in selected_cards:

            discard_selection.append(
                index
            )

            if len(discard_selection) == 2:
                break

    # --------------------------------------------------------
    # Сносим карты.
    # --------------------------------------------------------

    discarded_cards = [
        hand[index]
        for index in discard_selection
    ]

    player_hands[declarer] = [
        card
        for index, card in enumerate(hand)
        if index not in discard_selection
    ]

    discard_selection.clear()

    print(
        "СНОС ИИ:",
        declarer,
        "| контракт:",
        declarer_contract,
        "| снес:",
        discarded_cards
    )

    # --------------------------------------------------------
    # Следующий этап.
    # --------------------------------------------------------

    if declarer_contract == "Мизер":

        whist_current_player = (
            declarer + 1
        ) % 3

        whist_actions = ["", ""]

        game_phase = "whist"

    else:

        game_phase = "contract"

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

def bot_make_contract():

    global declarer_contract
    global game_phase
    global whist_current_player
    global whist_actions

    if game_phase != "contract":
        return

    if declarer == 0:
        return

    if declarer is None:
        return

    hand = player_hands[declarer]

    if len(hand) != 10:
        return

    available_contracts = get_available_contracts()

    if not available_contracts:
        return

    # --------------------------------------------------------
    # Оцениваем доступные контракты уже по настоящей
    # руке после получения прикупа и сноса.
    #
    # Используем и силу руки, и симуляцию розыгрыша.
    # --------------------------------------------------------

    evaluations = []

    for contract in available_contracts:

        confidence = analyze_hand_for_contract(
            hand,
            contract
        )

        probability, average_tricks = (
            estimate_contract_probability(
                hand,
                contract,
                120
            )
        )

        evaluations.append(
            (
                contract,
                confidence,
                probability,
                average_tricks
            )
        )

    # --------------------------------------------------------
    # Показываем для отладки, что выбрал ИИ.
    # --------------------------------------------------------

    print(
        "КОНТРАКТ ИИ:",
        declarer,
        "| рука:",
        hand
    )

    for contract, confidence, probability, average_tricks in evaluations:

        print(
            contract,
            "| уверенность:",
            round(confidence, 1),
            "| успех:",
            round(probability * 100, 1),
            "%",
            "| средние взятки:",
            round(average_tricks, 2)
        )

    # --------------------------------------------------------
    # Для разных уровней требуется разная сила руки
    # и разная вероятность выполнения контракта.
    #
    # Чем выше контракт, тем выше должны быть
    # оба показателя.
    # --------------------------------------------------------

    required_confidence = {
        6: 0,
        7: 22,
        8: 40,
        9: 50,
        10: 60
    }

    required_probability = {
        6: 0.45,
        7: 0.30,
        8: 0.40,
        9: 0.55,
        10: 0.65
    }

    reasonable = []

    for item in evaluations:

        contract = item[0]
        confidence = item[1]
        probability = item[2]

        suit, level = get_bid_contract(
            contract
        )

        target_confidence = required_confidence.get(
            level,
            32
        )

        target_probability = required_probability.get(
            level,
            0.20
        )

        if (
            confidence >= target_confidence
            and probability >= target_probability
        ):

            reasonable.append(item)

    if reasonable:

        max_level = max(
            get_bid_contract(
                item[0]
            )[1]
            for item in reasonable
        )

        same_level = [
            item
            for item in reasonable
            if get_bid_contract(
                item[0]
            )[1] == max_level
        ]

        same_level.sort(
            key=lambda item: item[2]
        )

        selected_contract = same_level[-1][0]

    else:

        # Если ни один контракт не прошёл основные
        # пороги, не позволяем слабой руке автоматически
        # уйти в высокий контракт только из-за симуляции.
        #
        # Для 6-го уровня достаточно положительной
        # вероятности.
        #
        # Для 7-го и выше требуется хотя бы минимальная
        # уверенность в самой руке.

        fallback_evaluations = []

        for item in evaluations:

            contract = item[0]
            confidence = item[1]
            probability = item[2]

            suit, level = get_bid_contract(
                contract
            )

            if probability <= 0:

                continue

            if level == 10 and confidence < 60:

                continue

            if level == 9 and confidence < 50:

                continue

            if level == 8 and confidence < 40:

                continue

            if level == 7 and confidence < 25:

                continue

            fallback_evaluations.append(item)

        if fallback_evaluations:

            max_average_tricks = max(
                item[3]
                for item in fallback_evaluations
            )

            close_evaluations = [
                item
                for item in fallback_evaluations
                if item[3] >= max_average_tricks - 0.20
            ]

            close_evaluations.sort(
                key=lambda item: (
                    item[1],
                    item[3]
                )
            )

            selected_contract = close_evaluations[-1][0]

        else:

            # Если даже 7+ не имеют достаточной
            # уверенности, выбираем только среди
            # контрактов 6-го уровня.

            level_six = [
                item
                for item in evaluations
                if (
                    get_bid_contract(
                        item[0]
                    )[1] == 6
                    and item[2] > 0
                )
            ]

            if level_six:

                level_six.sort(
                    key=lambda item: (
                        item[1],
                        item[3]
                    )
                )

                selected_contract = level_six[-1][0]

            else:

                evaluations.sort(
                    key=lambda item: (
                        item[3],
                        item[1]
                    )
                )

                selected_contract = evaluations[-1][0]

    declarer_contract = selected_contract

    print(
        "КОНТРАКТ ИИ:",
        declarer,
        "| выбрал:",
        declarer_contract
    )

    # --------------------------------------------------------
    # Переходим к висту.
    # --------------------------------------------------------

    whist_current_player = (
        declarer + 1
    ) % 3

    whist_actions = ["", ""]

    game_phase = "whist"

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

        print(
            "ВИСТ: ИИ",
            player,
            "| score:",
            score,
            "| threshold:",
            threshold
        )

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
    global whist_choice
    global play_current_player
    global trick_lead_suit
    global trick_winner
    global trick_pause
    global trick_pause_start
    global trick_number

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
                    # Кнопка выхода
                    # ----------------------------------------

                    if exit_button_rect.collidepoint(
                        event.pos
                    ):

                        running = False

                    # ----------------------------------------
                    # Торговля
                    # ----------------------------------------

                    elif game_started and bidding_active:

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

                                print(
                                    "ПРОВЕРКА ПЛАШКИ:",
                                    "whist_choice =",
                                    whist_choice
                                )

                                whist_current_player = (
                                    whist_current_player + 1
                                ) % 3

                                if all(
                                    value != ""
                                    for value in whist_actions
                                ):

                                    start_play_phase()

                                break

                    elif (
                        game_started
                        and game_phase == "play"
                        and not trick_pause
                    ):

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

                                    same_suit_cards = [
                                        hand_card
                                        for hand_card in player_hands[0]
                                        if hand_card[1] == trick_lead_suit
                                    ]

                                    if (
                                        trick_cards
                                        and same_suit_cards
                                        and card[1] != trick_lead_suit
                                    ):
                                        break

                                    print(
                                        "РОЗЫГРЫШ: игрок 0 сыграл:",
                                        card
                                    )

                                    trick_cards.append(
                                        (0, card)
                                    )

                                    if len(trick_cards) == 1:

                                        trick_lead_suit = card[1]

                                    played_cards.append(
                                        (0, card)
                                    )

                                    player_hands[0].remove(
                                        card
                                    )

                                    if len(trick_cards) == 3:

                                        trick_winner = determine_trick_winner()

                                        tricks_won[trick_winner] += 1

                                        print(
                                            "РОЗЫГРЫШ: взятку взял:",
                                            trick_winner
                                        )

                                        trick_pause = True
                                        trick_pause_start = pygame.time.get_ticks()

                                    else:

                                        play_current_player = (
                                            play_current_player + 1
                                        ) % 3

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

                                whist_current_player = (
                                    declarer + 1
                                ) % 3

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
        # Кнопка выхода
        # ----------------------------------------------------

        draw_exit_button(screen)

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
                game_phase == "talon"
                and declarer != 0
            ):
                take_talon()

            if (
                game_phase == "whist"
                and whist_current_player != 0
            ):

                bot_make_whist()

            if (
                game_phase == "discard"
                and declarer != 0
            ):

                bot_make_discard()

            if (
                game_phase == "contract"
                and declarer != 0
            ):

                bot_make_contract()

            if (
                game_phase == "play"
                and play_current_player != 0
                and not trick_pause
            ):

                bot_make_play()
            if trick_pause:

                if (
                    pygame.time.get_ticks()
                    - trick_pause_start
                    >= 2050
                ):

                    played_cards.clear()
                    trick_cards.clear()

                    trick_lead_suit = None

                    trick_pause = False
                    trick_pause_start = 0

                    if trick_number == 10:

                        game_phase = "result"

                        print(
                            "РОЗЫГРЫШ: все 10 взяток сыграны"
                        )

                    else:

                        trick_number += 1

                        play_current_player = trick_winner

                        print(
                            "РОЗЫГРЫШ: следующий ход:",
                            play_current_player
                        )
            draw_game_cards(screen)
            draw_opponent_actions(screen)
            draw_player_action(screen)
            draw_players(screen)

            # ------------------------------------------------
            # Стрелка победителя взятки
            # ------------------------------------------------

            if trick_pause:

                arrow_x = WIDTH // 2 + 110
                arrow_y = HEIGHT - 340

                arrow_color = (220, 40, 40)

                if trick_winner == 0:

                    # Вниз

                    pygame.draw.rect(
                        screen,
                        arrow_color,
                        (
                            arrow_x - 8,
                            arrow_y - 25,
                            16,
                            25
                        )
                    )

                    pygame.draw.polygon(
                        screen,
                        arrow_color,
                        [
                            (
                                arrow_x - 24,
                                arrow_y
                            ),
                            (
                                arrow_x + 24,
                                arrow_y
                            ),
                            (
                                arrow_x,
                                arrow_y + 30
                            )
                        ]
                    )

                elif trick_winner == 1:

                    # Влево

                    pygame.draw.rect(
                        screen,
                        arrow_color,
                        (
                            arrow_x - 5,
                            arrow_y - 8,
                            25,
                            16
                        )
                    )

                    pygame.draw.polygon(
                        screen,
                        arrow_color,
                        [
                            (
                                arrow_x - 30,
                                arrow_y
                            ),
                            (
                                arrow_x,
                                arrow_y - 24
                            ),
                            (
                                arrow_x,
                                arrow_y + 24
                            )
                        ]
                    )

                elif trick_winner == 2:

                    # Вправо

                    pygame.draw.rect(
                        screen,
                        arrow_color,
                        (
                            arrow_x - 20,
                            arrow_y - 8,
                            25,
                            16
                        )
                    )

                    pygame.draw.polygon(
                        screen,
                        arrow_color,
                        [
                            (
                                arrow_x + 30,
                                arrow_y
                            ),
                            (
                                arrow_x,
                                arrow_y - 24
                            ),
                            (
                                arrow_x,
                                arrow_y + 24
                            )
                        ]
                    )

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
