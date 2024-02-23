from abc import ABC, abstractmethod
from typing import cast

from pygame.event import Event
from pygame import Surface, display


class BaseDrawObject(ABC):
    """
    Базовый класс для отображаемых объектов

    :param ctx: Контекст для рисования
    """

    def __init__(self, ctx: Surface) -> None:
        self.ctx = ctx

    @abstractmethod
    def draw(self) -> None:
        """
        Абстрактный метод для формирования изображения объекта. Должен быть переопеределен в наследнике
        """
        pass


class DrawObject(BaseDrawObject, ABC):
    """
    Базовый класс для отображаемых объектов

    :param ctx: Контекст для рисования
    :param left_top: Позиция левого верхнего угла объкта
    """

    def __init__(self, ctx: Surface, left_top: tuple[int, int] = (0, 0)) -> None:
        super().__init__(ctx)
        self.screen = display.get_surface()
        self.left_top = left_top

    def local_pos(self, pos: tuple[int, int]) -> tuple[int, int]:
        """
        Преобразование позиции курсора в локальную позицию объекта

        :param pos: Глобальная позиция курсора
        :return: Локальная позиция объекта
        """
        return cast(tuple[int, int], tuple([i - j for i, j in zip(pos, self.left_top)]))

    def update(self, events: list[Event]) -> any:
        """
        Обработка событий Event

        :param events: Список событий
        """
        pass

    def paint(self):
        """
        Метод для отрисовки объекта на экране
        """
        self.draw()
        self.screen.blit(self.ctx, self.left_top)
