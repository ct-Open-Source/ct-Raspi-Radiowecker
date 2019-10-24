import pygame
from .aspect_scale import *
from .ptext import *

fontcolor = pygame.Color(255, 255, 255, 255)
background = pygame.Color(0, 0, 0, 128)
transparent = pygame.Color(0, 0, 0, 0)


class GuiObject(object):
    Surface = None
    Dirty = False
    _Position = (0, 0)

    @property
    def Position(self):
        return self._Position

    @Position.setter
    def Position(self, new_value):
        self._Position = new_value
        top_x = self._Position[0]
        top_y = self._Position[1]
        self.Rect = pygame.Rect(
            top_x, top_y, self.Surface.get_width(), self.Surface.get_height())


class Image(GuiObject):
    def __init__(self, image, size=None):
        if size != None:
            self.Surface = aspect_scale(image, size)
        else:
            self.Surface = image
        self.Surface.convert_alpha()

    @property
    def Position(self):
        return super().Position

    @Position.setter
    def Position(self, new_value):
        super(Image, self.__class__).Position.fset(self, new_value)


class Text(GuiObject):
    def __init__(self, text, size, font=None, color=fontcolor, shadow=True, shadowoffset=(1, 1), shadowcolor=background, wrapwidth=None, boxrect=None):
        if not shadow:
            shadowoffset = None
            shadowcolor = None
        if text != "":
            if boxrect != None:
                surface, rect = drawbox(text, (0, 0), color=color, background=None,
                                        fontname=font, surf=None, shadow=shadowoffset, scolor=shadowcolor)
            else:
                surface, rect = draw(text, (0, 0), color=color, background=None,
                                     fontsize=size, fontname=font, surf=None, shadow=shadowoffset, scolor=shadowcolor, widthem=wrapwidth)
        else:
            surface = pygame.Surface((0, 0), flags=pygame.SRCALPHA)

        self.Surface = surface.convert_alpha()

    @property
    def Position(self):
        return super().Position

    @Position.setter
    def Position(self, new_value):
        super(Text, self.__class__).Position.fset(self, new_value)


class Button(GuiObject):
    Surface = None
    _Position = (0, 0)

    def __init__(self, image, size=None,  callback=None, dblclk_callback=None):
        self.Callback = callback
        self.DblclkCallback = dblclk_callback
        if size == None:
            self.Surface = image
        else:
            self.Surface = aspect_scale(image, size)

        self.Surface.convert_alpha()

    @property
    def Position(self):
        return super().Position

    @Position.setter
    def Position(self, new_value):
        super(Button, self.__class__).Position.fset(self, new_value)


if __name__ == "__main__":
    print("This module cannot be called directly.")
