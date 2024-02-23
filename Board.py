from pygame import draw, Surface
from pygame.font import Font
from pygame.mixer import Sound
from pygame.event import Event, post
import pygame.constants

from copy import copy
from random import randint
from datetime import datetime
from typing import Self, Optional
from enum import IntEnum, Enum
from itertools import groupby
from collections import defaultdict

from System import resource_path
from DrawObject import BaseDrawObject, DrawObject
from HighScore import HighScore
from Colors import NONE, BLACK, RED, GREEN, BLUE, CYAN, MAGENTA, YELLOW, GRAY

FONT_M = resource_path(r'fonts/pt-mono.ttf')


class KEY(IntEnum):
    QUIT = pygame.K_ESCAPE
    HARD_DROP = pygame.K_SPACE
    DOWN = pygame.K_DOWN
    LEFT = pygame.K_LEFT
    RIGHT = pygame.K_RIGHT
    ROTATE_RIGHT = pygame.K_UP
    ROTATE_LEFT = pygame.K_q
    PLAY = pygame.K_RETURN
    PAUSE = pygame.K_p
    SOUND_FX = pygame.K_s


class Piece(BaseDrawObject):
    """
    Фигура


    :param ctx: Контекст для рисования
    :param p: Позиция
    :param type_id: Тип
    """

    class ROTATION(Enum):
        LEFT = 'left'
        RIGHT = 'right'

    SHAPES = (
        (),
        ((0, 1, 0),
         (0, 1, 0),
         (0, 1, 0)),
        ((0, 1),
         (1, 1)),
        ((1, 0),
         (1, 0)),
        ((1,),)
    )
    COLORS = (
        NONE,
        CYAN,
        BLUE,
        YELLOW,
        GREEN,
        MAGENTA,
        RED
    )
    MOVES = {
        KEY.LEFT: lambda p: p.offset(-1, 0),
        KEY.RIGHT: lambda p: p.offset(1, 0),
        KEY.DOWN: lambda p: p.offset(0, 1),
        KEY.HARD_DROP: lambda p: p.offset(0, 1),
        KEY.ROTATE_RIGHT: lambda p: p.rotate(Piece.ROTATION.RIGHT),
        KEY.ROTATE_LEFT: lambda p: p.rotate(Piece.ROTATION.LEFT)
    }

    def __init__(self, ctx, p: tuple[int, int] = (0, 0), type_id: int = 0):
        super().__init__(ctx)
        self.typeId = type_id if type_id != 0 else self.randomize_piece_type(len(Piece.SHAPES) - 1)
        self.shape = [list(self.randomize_piece_type(len(Piece.COLORS) - 1) if c != 0 else 0 for c in e)
                      for e in Piece.SHAPES[self.typeId]]
        self.x, self.y = p
        self.hard_dropped = False

    def draw(self) -> None:
        for y, row in enumerate(self.shape):
            for x, value in enumerate(row):
                if value > 0:
                    rect = ((self.x + x) * Board.BLOCK_SIZE, (self.y + y) * Board.BLOCK_SIZE,
                            Board.BLOCK_SIZE + Board.BORDER_WIDTH, Board.BLOCK_SIZE + Board.BORDER_WIDTH)
                    draw.rect(self.ctx, Piece.COLORS[value], rect)
                    draw.rect(self.ctx, BLACK, rect, width=Board.BORDER_WIDTH)

    def moves(self, key: KEY) -> Optional[Self]:
        """
        Выполняет перемещение тетрамино

        :param key: Вид перемещения
        :return: Новый объект тетрамино с выполненным перемещением
        """
        return Piece.MOVES[key](self) if key in Piece.MOVES else None

    def move(self, p: Self) -> None:
        """
        Перемещает татрамино в позицию переданного

        :param p: Тетрамино
        """
        if not self.hard_dropped:
            self.x, self.y = p.x, p.y
        self.shape = p.shape

    def hard_drop(self) -> None:
        """
        Устанавливает признах hard_dropped
        """
        self.hard_dropped = True

    def set_starting_position(self) -> None:
        """
        Задает начальную позицию в зависимости от типа тетрамино
        """
        self.x = 2 if self.typeId < 3 else 3

    @staticmethod
    def randomize_piece_type(no_of_types: int) -> int:
        """
        Получает случайный тип тетрамино

        :param no_of_types: Количесво типов
        :return: Тип
        """
        return randint(0, no_of_types - 1) + 1

    def offset(self, x: int, y: int) -> Self:
        """
        Создает копию тетрамиро с изменением координаты

        :param x: x
        :param y: y
        :return: Копия тетрамино
        """
        p = copy(self)
        p.shape = [list(e) for e in p.shape]
        p.x += x
        p.y += y
        return p

    def rotate(self, direction: ROTATION) -> Self:
        """
        Создает копию тетрамиро с вращением

        :param direction: Направление вращения
        :return: Копия тетрамино
        """
        p = copy(self)
        if not p.hard_dropped:
            # Transpose matrix
            p.shape = [list(e) for e in zip(*p.shape)]
            # Reverse the order of the columns.
            if direction == Piece.ROTATION.RIGHT:
                p.shape = [row[::-1] for row in p.shape]
            elif direction == Piece.ROTATION.LEFT:
                p.shape = p.shape[::-1]
        else:
            p.shape = [list(e) for e in p.shape]
        return p


class Board(DrawObject):
    """
    Игровое поле

    :param ctx: Контекст для рисования
    :param left_top: Позиция левого верхнего угла объкта
    :param ctx_next: Контекст для вывода следующей фигуры
    :param high_score: Ссылка на объект HighScore
    """
    COLS = 7
    ROWS = 18
    BLOCK_SIZE = 50
    BORDER_WIDTH = 2

    POINTS = (
        {3: 40, 4: 120, 5: 440, 6: 1560, 7: 5560},
        {3: 50, 4: 150, 5: 550, 6: 1950, 7: 6950},
        {3: 75, 4: 225, 5: 825, 6: 2925, 7: 10425}
    )

    # LEVEL = (800, 720, 630, 550, 470, 380, 300, 220, 130, 100, 80, 80, 80, 70, 70, 70, 50, 50, 50, 30, 30)
    LEVEL = (800, 730, 660, 590, 530, 470, 410, 360, 310, 260, 220, 180, 140, 110, 100, 90, 90, 90, 90, 80, 80)

    class SOUNDS(Enum):
        DROP = 'drop'
        FINISH = 'finish'
        MOVES = 'moves'
        POINTS = 'points'

    MAX_OPACITY = 15
    TIME_PER_LEVEL = 59

    class Field:
        def __init__(self, color: int = 0):
            self.color = color
            self.selected = False

        def __bool__(self):
            return self.selected

        def __repr__(self):
            return f"{'-' if self.selected else ''}{self.color}"

    def __init__(self, ctx, left_top, ctx_next: Surface, high_score: HighScore):
        super().__init__(ctx, left_top)
        self.font = Font(FONT_M, 24)

        self.music = {e: Sound(resource_path(f"sounds/{e.value}.mp3")) for e in Board.SOUNDS}

        self.play_sound_fx = False

        self.ctx_next = ctx_next
        self.high_score = high_score
        self.grid: list[list[Board.Field]] = []
        self.piece = None
        self.next = None

        self.opacity = 0
        self._pause = True
        self._game_over = True

        self.level = 0
        self.score = 0

        self.now = datetime.now()
        self.hard_drop = False

        self.level_time = datetime.now()
        self.level_cnt = 0

        self.bonus_list = []
        self.bonus = 0

        self.reset()

        self._game_over = None

    def play(self, sound: SOUNDS) -> None:
        """
        Проиuгрывает звук

        :param sound: Тип звука
        """
        if self.play_sound_fx:
            self.music[sound].play()

    @property
    def pause(self):
        return self._pause

    @pause.setter
    def pause(self, value):
        self._pause = value
        if not self._pause and self.game_over is None:
            self._game_over = False

    @property
    def game_over(self) -> bool:
        return self._game_over

    @game_over.setter
    def game_over(self, value: bool):
        if value:
            if not self._game_over:
                self.play(Board.SOUNDS.FINISH)
                self.high_score.add_score(self.score)
        self._game_over = value

    def reset(self) -> None:
        self.grid = self.get_empty_grid()
        self.piece = Piece(self.ctx)
        self.piece.set_starting_position()
        self.get_new_piece()

        self.opacity = 0
        self.pause = True
        self.game_over = False

        self.level = 0
        self.score = 0

        self.now = datetime.now()
        self.hard_drop = False

        self.level_time = datetime.now()
        self.level_cnt = 0

    def get_new_piece(self) -> None:
        self.next = Piece(self.ctx_next)

    def draw(self) -> None:
        self.ctx.fill(GRAY)
        if self.piece:
            self.piece.draw()
        self.draw_board()
        draw.rect(self.ctx, BLACK, (0, 0, self.ctx.get_width(), self.ctx.get_height()), width=2)

    def draw_board(self) -> None:
        def opacity(color):
            return [e - e * (Board.MAX_OPACITY - self.opacity + 1) // Board.MAX_OPACITY for e in color]

        for x, col in enumerate(self.grid):
            for y, value in enumerate(col):
                if value.color > 0:
                    rect = (x * Board.BLOCK_SIZE, y * Board.BLOCK_SIZE,
                            Board.BLOCK_SIZE + Board.BORDER_WIDTH, Board.BLOCK_SIZE + Board.BORDER_WIDTH)
                    color = opacity(Piece.COLORS[value.color]) \
                        if self.opacity and value.selected else Piece.COLORS[value.color]
                    draw.rect(self.ctx, color, rect)
                    draw.rect(self.ctx, BLACK, rect, width=Board.BORDER_WIDTH)

    def drop(self) -> None:
        if self.opacity != 0:
            if self.opacity < 0:
                self.opacity = 0
            else:
                self.opacity -= 1
            if self.opacity == 0:
                self.opacity = 0
                self.clear_lines()
                if bonus_type := self.select_grid():
                    self.opacity = Board.MAX_OPACITY
                    self.bonus_list.append(bonus_type)
                else:
                    if self.bonus_list:
                        if len(self.bonus_list) > 1:
                            self.bonus = 500 + 1000 * (len(self.bonus_list) - 2) + (500 if 2 in self.bonus_list else 0)
                            self.score += self.bonus
                        self.bonus_list.clear()
                    if self.piece.y == 0:
                        self.game_over = True
                    else:
                        self.piece = self.next
                        self.piece.ctx = self.ctx
                        self.piece.set_starting_position()
                        self.get_new_piece()
                self.now = datetime.now()
        else:
            self.bonus = 0
            if not self.pause and not self.game_over:
                d = (datetime.now() - self.level_time)
                if d.seconds > 0:
                    self.level_time = datetime.now()
                    self.level_cnt += 1
                    if self.level_cnt > Board.TIME_PER_LEVEL:
                        self.level_cnt = 0
                        self.level += 1
                if self.hard_drop:
                    self.hard_drop = False
                else:
                    d = (datetime.now() - self.now)
                    if not (d.seconds > 1 or d.microseconds > Board.LEVEL[self.level] * 1000):
                        return
                p = self.piece.moves(KEY.DOWN)
                if self.valid(p):
                    self.piece = p
                    self.now = datetime.now()
                else:
                    self.freeze()
                    if self.level > 5:
                        self.score += self.level - 5
                    if bonus_type := self.select_grid():
                        self.opacity = Board.MAX_OPACITY
                        self.bonus_list.append(bonus_type)
                    else:
                        self.opacity = -1

    def clear_lines(self) -> None:
        for col in self.grid:
            if any(col):
                last_empty = 0
                for y, value in enumerate(col):
                    if value.selected:
                        col.pop(y)
                        col.insert(last_empty, Board.Field())
                    elif value.color == 0:
                        last_empty = y

    def valid(self, piece: Piece) -> bool:
        for dy, row in enumerate(piece.shape):
            for dx, value in enumerate(row):
                x = piece.x + dx
                y = piece.y + dy
                if not (value == 0 or (self.is_inside_walls(x, y) and self.not_occupied(x, y))):
                    return False
        return True

    def move(self, key: KEY) -> None:
        if not self.pause and not self.game_over:
            p = self.piece.moves(key)
            if p:
                if key == KEY.HARD_DROP:
                    # Hard drop
                    self.hard_drop = True
                    self.play(Board.SOUNDS.DROP)
                    while self.valid(p):
                        self.piece.move(p)
                        p = self.piece.moves(key)
                    self.piece.hard_drop()
                elif self.valid(p):
                    self.play(Board.SOUNDS.MOVES)
                    self.piece.move(p)

    def select_grid(self) -> int:
        """
        Отметка в матрице групп элементов с длиной более 3

        :return: Тип бонуса:
        0, если групп нет; 1, если есть только одна группа длиной 3; 2 в остальных случаях
        """
        def diagonals_left() -> list[list[Board.Field]]:
            """
            Преобразует матрицу в диагональную с направлением лево-верх - право-низ

            - rows - количество строк
            - cols - количество колонок
            - offset - отступ
            - matrix - исходная матрица

            :return: Преобразованная матрица
            """
            rows = Board.COLS
            cols = Board.ROWS
            offset = 2
            matrix = self.grid
            result = [[] for i in range(rows + cols - 1 - offset * 2)]
            k = rows - 1 - offset
            for i in range(-k, cols - offset):
                for j in range(rows):
                    row, col = j, i + j
                    if 0 <= row < rows and 0 <= col < cols:
                        result[i + k].append(matrix[row][col])
            return result

        def diagonals_right() -> list[list[Board.Field]]:
            """
            Преобразует матрицу в диагональную с направлением право-верх - лево-низ

            - rows - количество строк
            - cols - количество колонок
            - offset - отступ
            - matrix - исходная матрица

            :return: Преобразованная матрица
            """
            rows = Board.COLS
            cols = Board.ROWS
            offset = 2
            matrix = self.grid
            result = [[] for i in range(rows + cols - 1 - offset * 2)]
            for i in range(offset, cols + rows - 1 - offset):
                for j in range(rows):
                    row, col = j, i - j
                    if 0 <= row < rows and 0 <= col < cols:
                        result[i - offset].insert(0, matrix[row][col])
            return result

        def transpose() -> list[list[Board.Field]]:
            """
            Транспонирование матрицы

            :return: Преобразованная матрица
            """
            return [list(e) for e in zip(*self.grid)]

        def check_grid(grid: list[list[Board.Field]], result: dict = None) -> dict:
            """
            Проверки на наличие групп одинаковых элеменов длиной более 3

            :param grid: Матрица для поиска
            :param result: Результирающий словарь для дополнения. Если не задан, то создается новый
            :return: Словарь вида {Длина: int -> Количество: int}
            """
            if result is None:
                result = defaultdict(int)
            for vector in grid:
                for key, value in groupby(vector, key=lambda x: x.color):
                    if key != 0:
                        if (line_len := len(value_list := tuple(value))) > 2:
                            result[line_len] += 1
                            for v in value_list:
                                v.selected = True
            return result

        lines_cnt = (
            check_grid(self.grid),
            check_grid(transpose()),
            check_grid(diagonals_right(), check_grid(diagonals_left()))
        )

        bonus_type = 0
        if any(lines_cnt):
            for direction, line_cnt in enumerate(lines_cnt):
                for line_len, cnt in line_cnt.items():
                    self.score += Board.POINTS[direction][line_len] * cnt
                    bonus_type = 2 if bonus_type > 0 or line_len > 3 else 1
        return bonus_type

    def freeze(self) -> None:
        for y, row in enumerate(self.piece.shape):
            for x, value in enumerate(row):
                if value > 0:
                    self.grid[x + self.piece.x][y + self.piece.y] = Board.Field(value)

    @staticmethod
    def get_empty_grid() -> list[list[Field]]:
        return [[Board.Field() for _ in range(Board.ROWS)] for _ in range(Board.COLS)]

    @staticmethod
    def is_inside_walls(x: int, y: int) -> bool:
        return 0 <= x < Board.COLS and y < Board.ROWS

    def not_occupied(self, x: int, y: int) -> bool:
        return self.grid[x][y].color == 0

    def update(self, events: list[Event]):
        for event in events:
            match event.type:
                case pygame.KEYDOWN:
                    match event.key:
                        case KEY.QUIT:
                            if self.game_over or self.game_over is None:
                                post(Event(pygame.QUIT))
                            else:
                                self.game_over = True
                        case KEY.PLAY:
                            if self.game_over:
                                self.reset()
                                self.pause = False
                            elif self.game_over is None:
                                self.pause = False
                        case KEY.PAUSE:
                            if not (self.game_over is None or self.game_over):
                                self.pause = not self.pause
                        case KEY.SOUND_FX:
                            self.play_sound_fx = not self.play_sound_fx
                        case _:
                            self.move(event.key)
