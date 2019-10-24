#!/usr/bin/python
#  -*- coding: utf-8 -*-
import pygame.freetype
import pygame
import os
import math
import datetime
import glob
from time import time
from .toolkit import *
from .aspect_scale import *
from .gradient import *
from time import time, sleep


class Gui:
    def __init__(self, display_resolution, fg_color, bg_color,
                 cursor_visible, quit_function):
        pygame.init()
        pygame.mixer.quit()
        # a fullscreen switch for debugging purposes
        self.fullscreen = False
        # the display resolution as a tuple
        self.display_size = (int(display_resolution.split(
            ',')[0]), int(display_resolution.split(',')[0]))
        # colors for foreground and background
        self.fg_color = self.string_to_color(fg_color)
        self.bg_color = self.string_to_color(bg_color)
        # the window size if the program is not set for fullscreen and no resolution was set
        self.window_size = (800, 480)
        # should the mouse cursor be visible?
        if cursor_visible != "1": pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))
        # correction factor for text elements
        # variables for resource files
        self.resource_path = "assets/"

        self.wallpaper_path = "."
        self.show_wallpaper = True

        self.basefont_file = self.resource_path + "SourceSansPro-Regular.otf"
        self.boldfont_file = self.resource_path + "SourceSansPro-Semibold.otf"
        self.logo_image = self.resource_path + "alarm-clock.png"
        self.image_cache = {}
        self.elements = []
        # start the gui
        self.set_window_details()
        self.display_init()
        self.calculate_base_sizes()

        self.old_time = 0
        self.fps_counter = 1
        self.target_framerate = 30

        self.clock = pygame.time.Clock()
        self.dblclktime = 200
        self.clicktime = 0
        self.await_dblclk = False
        self.clickEvent = None
        self.click = None
        self.redraw = True

    # initialize the display surface
    def display_init(self):
        # try to create a surface and check if it fails
        try:
            # fullscreen is the default
            if self.fullscreen:
                # create a hardware accelerated fullscreen surface
                self.display_surface = pygame.display.set_mode(
                    self.display_size, pygame.FULLSCREEN)
            # alternatively try a windowed surface
            else:
                self.display_surface = pygame.display.set_mode(size=self.window_size,
                                                               flags=pygame.RESIZABLE, display=1)
        except Exception as exc:
            print(exc)
            print("Display initialization failed. This program needs a running X-Server.")
            exit()

        self.loadImageCache()
        # get absolute size of the surface independend from what was
        # requested.
        self.display_size = self.display_surface.get_size()

        self.current_wallpaper_surface = pygame.image.load(
            self.wallpaper_path + "/wallpaper.jpg")
        self.current_wallpaper_surface = aspect_scale(
            self.current_wallpaper_surface, self.display_size).convert()

    def loadImageCache(self):
        image_list = glob.glob(self.resource_path+'/*.png')
        for image in image_list:
            path, filename = os.path.split(image)
            self.image_cache[filename] = pygame.image.load(
                image).convert_alpha()

    def display_resize(self):
        self.display_init()
        self.calculate_base_sizes()

    # set the window caption and the icon
    def set_window_details(self):
        pygame.display.set_caption("c't Radio Alarm Clock")
        icon = pygame.image.load(self.logo_image)
        pygame.display.set_icon(icon)

    def calculate_base_sizes(self):
        # calculate the sizes of displayed elements based on the available
        # display resolution.
        # the size of the titlebar is an essential measurement and determines
        # most other measurements
        self.basefont_size = self.display_size[0] / 30
        pass

    def calculate_object_size(self, width_percentage, height_percentage):
        width = math.floor(self.display_size[0] * width_percentage / 100)
        height = math.floor(self.display_size[1] * height_percentage / 100)

        return (width, height)

    def calculate_position(self, percentage, surface, origin_v="top", origin_h="left"):
        surface_size = surface.get_size()
        origin_shift_x = 0
        origin_shift_y = 0
        if origin_v == "center":
            origin_shift_y = (
                self.display_size[1] / 2) - (surface_size[1] / 2)
        elif origin_v == "bottom":
            origin_shift_y = self.display_size[1] - surface_size[1]

        if origin_h == "center":
            origin_shift_x = (
                self.display_size[0] / 2) - (surface_size[0] / 2)
        elif origin_h == "right":
            origin_shift_x = self.display_size[0] - surface_size[0]
        top_pos = ((percentage[0] / 100) *
                   self.display_size[0]) + origin_shift_y
        left_pos = ((percentage[1] / 100) *
                    self.display_size[1]) + origin_shift_x
        return (left_pos, top_pos)

    def calculate_font_size(self, percentage):
        fontsize = tuple((percentage / 100) * x for x in self.display_size)
        return fontsize[0]

    # refresh the display

    def update(self):
        self.process_events()
        # paint the background color or wallpaper
        if not self.show_wallpaper:
            self.display_surface.fill(self.bg_color)
        else:
            self.display_surface.blit(self.current_wallpaper_surface, (0, 0))
        # iterate all surfaces and paint them
        rects = []
        for element in self.elements:
            image_pos_x = element.Position[0]
            image_pos_y = element.Position[1]
            rects.append(element.Rect)

            self.display_surface.blit(
                element.Surface, (image_pos_x, image_pos_y))
        # flip the screen for a refreh
        if self.redraw:
            pygame.display.update()
            self.redraw = False
        else:
            pygame.display.update(rects)
        # self.show_fps()
        self.clock.tick(self.target_framerate)

    def show_fps(self):
        new_time = int(time())
        if new_time != self.old_time:
            print("FPS:" + str(int(self.clock.get_fps())))
            self.old_time = new_time

    def quit(self):
        # cleanly deactivate the pygame instance
        self.quit_function()

    # process all received events

    def process_events(self):
        clicked = False
        events = pygame.event.get()
        for event in events:
            # if the event is any type of quit request end the program
            if event.type == pygame.QUIT:
                quit()

            # resize the window if its requested
            elif event.type == pygame.VIDEORESIZE:
                self.window_size = event.size
                self.display_resize()

            # evaluate keypresses
            elif event.type == pygame.KEYDOWN:
                # exit on Escape
                if event.key == pygame.K_ESCAPE:
                    quit()
                # switch to fullscreen on F11
                elif event.key == pygame.K_F11:
                    self.fullscreen = not self.fullscreen

            # evaluate all presses of the left mousebutton
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                clicked = True
                self.clicktime = pygame.time.get_ticks()
                self.clickEvent = event

        click = None
        timediff = pygame.time.get_ticks() - self.clicktime
        if clicked and self.await_dblclk == False and self.click == None:
            self.await_dblclk = True
            pass
        elif clicked and timediff < self.dblclktime and self.await_dblclk:
            click = "double"
            self.await_dblclk = False
        elif timediff > self.dblclktime and self.await_dblclk:
            click = "single"
            self.await_dblclk = False
        if click != None:
            self.await_dblclk = False
            self.clicktime = 0
            for element in self.elements:
                if hasattr(element, 'Callback') and element.Callback != None and element.Rect.collidepoint(self.clickEvent.pos):
                    if click == "double" and element.DblclkCallback != None:
                        element.DblclkCallback()
                    else:
                        element.Callback()

    # exit the programm

    def shutdown(self):
        # call(["sudo", "poweroff"])
        self._running = False

    # convert a given comma seperated string to a color object

    def string_to_color(self, string):
        # split the string into a list
        list = string.split(',')
        # create color from the list indices
        color = pygame.Color(
            int(list[0]),
            int(list[1]),
            int(list[2])
        )
        # return the created color object
        return color


if __name__ == "__main__":
    print("This module cannot be called directly.")
