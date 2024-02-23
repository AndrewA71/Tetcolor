from pygame import display, Rect
from pygame.font import Font
from pygame.event import get
import pygame.constants

import operator
from dataclasses import dataclass
from pathlib import Path
import time

from System import resource_path
from DrawObject import DrawObject
from Colors import BLACK, WHITE, RED, YELLOW, GREEN, CYAN, BLUE

FONT_M = resource_path(r'fonts/pt-mono.ttf')


@dataclass
class Score:
    Score: int
    Name: str


class HighScore(DrawObject):
    """
    Рекорды
    """

    NO_OF_HIGH_SCORES = 30

    LEFT_OFFSET = 4
    TOP_OFFSET = 2
    MAX_LENGTH = 11

    def __init__(self, ctx, left_top):
        """

        :param ctx: Контекст для рисования
        :param left_top: Позиция левого верхнего угла объкта
        """
        super().__init__(ctx, left_top)
        self.font_m = Font(FONT_M, 24)
        self.char_size = self.font_m.size(' ')
        self.file = Path('highscores.txt')
        self.scores: list[Score] = []
        if self.file.is_file():
            with open(self.file, 'r', encoding='utf-8') as file:
                for line in file:
                    score_name = line.strip().split('\t')
                    if len(score_name) == 2:
                        (score, name) = score_name
                    else:
                        score = line
                        name = ''
                    score = int(score)
                    self.scores.append(Score(score, name))

    def draw(self) -> None:
        self.ctx.fill(BLACK)
        width = self.ctx.get_width()

        char_width, char_height = self.char_size
        top_offset = char_height
        left_offset = char_width * HighScore.LEFT_OFFSET

        self.font_m.set_italic(True)
        text_surface = self.font_m.render(f'Top - {HighScore.NO_OF_HIGH_SCORES}', True, WHITE)
        self.ctx.blit(text_surface, ((width - text_surface.get_width()) // 2, top_offset))
        top_offset += char_height * HighScore.TOP_OFFSET

        for index, score in enumerate(self.scores +
                                      [Score(0, 'TETCOLOR')] * (HighScore.NO_OF_HIGH_SCORES - len(self.scores))):
            if index < 1:
                color = RED
            elif index < 3:
                color = YELLOW
            elif index < 10:
                color = GREEN
            elif index < 20:
                color = CYAN
            else:
                color = BLUE
            self.font_m.set_italic(False)
            text_surface = self.font_m.render(f"{index + 1:<2}  {score.Name:11}", True, color)
            self.ctx.blit(text_surface, (left_offset, top_offset))
            self.font_m.set_italic(True)
            text_surface = self.font_m.render(f"{score.Score:6}", True, color)
            self.ctx.blit(text_surface, (left_offset + char_width * 16, top_offset))
            top_offset += char_height

    def add_score(self, score: int) -> None:
        if score > 0 and (len(self.scores) < HighScore.NO_OF_HIGH_SCORES or score > self.scores[-1].Score):
            item = Score(score, '')
            self.scores.append(item)
            self.scores.sort(key=operator.attrgetter('Score'), reverse=True)
            a = self.scores.count(item)
            if len(self.scores) > HighScore.NO_OF_HIGH_SCORES:
                self.scores = self.scores[:HighScore.NO_OF_HIGH_SCORES]
            self.draw()
            name = self.show_input((self.char_size[0] * (HighScore.LEFT_OFFSET + 4),
                                    self.char_size[1] * (self.scores.index(item) + HighScore.TOP_OFFSET + 1)))
            item.Name = name if name else 'Anonymous'
            with open(self.file, 'w', encoding='utf-8') as file:
                for score in self.scores:
                    file.write(f"{score.Score}\t{score.Name}\n")

    def show_input(self, topleft: tuple[int, int]) -> str:
        self.font_m.set_italic(False)

        fill_rect = self.font_m.render(' ' * HighScore.MAX_LENGTH, True, WHITE).get_rect()
        fill_rect.topleft = topleft

        text = ''
        img = self.font_m.render(text, True, WHITE)
        text_rect = img.get_rect()
        text_rect.topleft = topleft
        cursor = Rect(text_rect.topright, (3, text_rect.height))

        clock = pygame.time.Clock()

        running = True
        while running:
            for event in get():
                match event.type:
                    case pygame.QUIT:
                        running = False
                    case pygame.KEYDOWN:
                        match event.key:
                            case pygame.K_BACKSPACE:
                                if len(text) > 0:
                                    text = text[:-1]
                            case pygame.K_RETURN | pygame.K_ESCAPE:
                                running = False
                            case _:
                                text += event.unicode
                                if len(text) == HighScore.MAX_LENGTH:
                                    running = False
                        img = self.font_m.render(text, True, WHITE)
                        text_rect.size = img.get_size()
                        cursor.topleft = text_rect.topright

            pygame.draw.rect(self.ctx, BLACK, fill_rect)
            self.ctx.blit(img, text_rect)
            if time.time() % 1 > 0.5:
                pygame.draw.rect(self.ctx, WHITE, cursor)
            self.screen.blit(self.ctx, self.left_top)
            display.update()
            clock.tick(100)

        return text
