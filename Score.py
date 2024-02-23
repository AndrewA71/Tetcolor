from pygame.font import Font, SysFont
from datetime import datetime

from System import resource_path
from DrawObject import DrawObject
from Board import Board
from Colors import BLACK, WHITE, BLUE, GREEN, YELLOW, RED

FONT = r'Times New Roman'
FONT_M = resource_path(r'fonts/pt-mono.ttf')


class Score(DrawObject):
    """
    Текущая информация об игре
    """

    def __init__(self, ctx, left_top, board: Board) -> None:
        """

        :param ctx: Контекст для рисования
        :param left_top: Позиция левого верхнего угла объкта
        :param board: Ссылка на объект Board
        """
        super().__init__(ctx, left_top)
        self.board = board
        self.font_m = Font(FONT_M, 24)
        self.font_m.set_italic(True)
        self.font_small = SysFont(FONT, 64)
        self.font_medium = SysFont(FONT, 80)
        self.font_large = SysFont(FONT, 128)

        self.tetcolor_sf = self.font_m.render('TETCOLOR', True, WHITE)
        self.game_sf = self.font_large.render('GAME', True, GREEN)
        self.over_sf = self.font_large.render('OVER', True, GREEN)
        self.pause_sf = self.font_large.render('PAUSE', True, GREEN)
        self.level_sf = self.font_small.render('LEVEL', True, BLUE)
        self.score_sf = self.font_small.render('SCORE', True, BLUE)
        self.bonus_sf = self.font_small.render('BONUS', True, RED)

        self.bonus = 0
        self.bonus_time = None
        self.bonus_cnt = 0

    def draw(self) -> None:
        self.ctx.fill(BLACK)
        width, height = self.ctx.get_size()

        char_width, char_height = self.font_m.size('1')
        top_offset = char_height

        # TETCOLOR
        self.ctx.blit(self.tetcolor_sf, ((width - self.tetcolor_sf.get_width()) // 2, top_offset))
        top_offset += self.tetcolor_sf.get_height() * 2

        # GAME OVER/PAUSE
        if self.board.game_over is not None and (self.board.game_over or self.board.pause):
            if self.board.game_over:
                self.ctx.blit(self.game_sf, ((width - self.game_sf.get_width()) // 2, top_offset))
                top_offset += self.game_sf.get_height()
                self.ctx.blit(self.over_sf, ((width - self.over_sf.get_width()) // 2, top_offset))
            elif self.board.pause:
                self.ctx.blit(self.pause_sf, ((width - self.pause_sf.get_width()) // 2, top_offset))

        # Score
        text_surface = self.font_medium.render(str(self.board.score), True, YELLOW)
        bottom_offset = self.ctx.get_height()
        bottom_offset -= self.score_sf.get_height() * 2
        self.ctx.blit(text_surface, ((width - text_surface.get_width()) // 2, bottom_offset))

        # Score title
        bottom_offset -= self.score_sf.get_height() * 1.5
        self.ctx.blit(self.score_sf, ((width - self.score_sf.get_width()) // 2, bottom_offset))

        # Level
        text_surface = self.font_medium.render(str(self.board.level + 1), True, GREEN)
        bottom_offset -= self.level_sf.get_height() * 1.5
        self.ctx.blit(text_surface, ((width - text_surface.get_width()) // 2, bottom_offset))

        # Level title
        bottom_offset -= self.level_sf.get_height() * 1.5
        self.ctx.blit(self.level_sf, ((width - self.level_sf.get_width()) // 2, bottom_offset))

        if self.board.bonus > 0 and self.bonus == 0:
            self.bonus = self.board.bonus
            self.bonus_time = datetime.now()
            self.bonus_cnt = 0

        if self.bonus > 0:
            d = (datetime.now() - self.bonus_time)
            if d.microseconds > self.bonus_cnt * 150000:
                self.bonus_cnt += 1

                if self.bonus_cnt > 6:
                    self.bonus = 0
                    return

            # Bonus
            text_surface = self.font_medium.render(str(self.bonus), True, YELLOW)
            bottom_offset -= self.level_sf.get_height() * 1.5
            if self.bonus_cnt % 2 != 0:
                self.ctx.blit(text_surface, ((width - text_surface.get_width()) // 2, bottom_offset))

            # Bonus title
            bottom_offset -= self.bonus_sf.get_height() * 1.5
            self.ctx.blit(self.bonus_sf, ((width - self.bonus_sf.get_width()) // 2, bottom_offset))
