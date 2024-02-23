from pygame import display, Surface, time, key
from pygame.event import get
import pygame.constants

from Board import Board
from HighScore import HighScore
from Score import Score


def main():
    width_list = (460, Board.BLOCK_SIZE * Board.COLS, 460)
    height = Board.BLOCK_SIZE * Board.ROWS
    width = sum(width_list)

    pygame.init()
    display.set_mode((width, height))
    display.set_caption("TETCOLOR")

    high_score = HighScore(Surface((width_list[0], height)), (sum(width_list[:2]), 0))
    board = Board(Surface((width_list[1], height)), (sum(width_list[:1]), 0),
                  Surface((Board.BLOCK_SIZE * 4, Board.BLOCK_SIZE * 2)), high_score)
    score = Score(Surface((width_list[2], height)), (0, 0), board)

    draw_objects = [high_score, board, score]

    clock = time.Clock()
    key.set_repeat(400, 25)

    running = True
    while running:
        for event in (events := get()):
            match event.type:
                case pygame.QUIT:
                    running = False

        [draw_object.update(events) for draw_object in draw_objects]
        board.drop()
        [draw_object.paint() for draw_object in draw_objects]

        display.flip()
        clock.tick(100)

    pygame.quit()


if __name__ == '__main__':
    main()
