#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pygame
import gui
import locale
from config import config
from mopidy import MusicPlayer
from alarm import Alarm
from datetime import datetime
import time
import threading


class application:

    def __init__(self):
        # load the config file
        self.config = config()
        self.ui = gui.Gui(
            self.config.setting["resolution"],
            self.config.setting["fg_color"],
            self.config.setting["bg_color"],
            self.config.setting["show_mouse_cursor"],
            quit_function = self.cleanup
        )
        locale.setlocale(locale.LC_ALL, self.config.setting["locale"]+".utf8")

        self.musicplayer = MusicPlayer(self.config.setting["mopidy_host"])
        self.alarm = Alarm(self.config.setting["alarmtime"], self.config.setting["snooze"], self.musicplayer)
        self.alarm.alarm_active = False
        if self.config.setting["enabled"] == "1":
            self.alarm.enableAlarm()
        else:
            self.alarm.disableAlarm()
        self.player_primed = False

        self.is_idle = False
        self.time_last_idle = time.time()
        self.check_idle_thread = threading.Thread(target=self.check_idle)
        self.check_idle_thread.daemon = True
        self.check_idle_thread.start()
        self.old_time = 0

        self.current_screen = self.idlescreen
        self.switch_to_defaultscreen()

        self.loop()

    def check_idle(self):
        while True:
            if time.time() - self.time_last_idle > 30:
                self.time_last_idle = time.time()
                self.is_idle = True
            time.sleep(1)

    def cleanup(self):
        print("bye")

    def cache_idlescreen(self):
        self.idlescreen_cache = {}
        time_string = datetime.now().strftime(
            self.config.setting["timeformat"])
        timefont_size = self.ui.calculate_font_size(30)
        fontcolor = pygame.color.Color(50, 50, 50, 255)
        self.idlescreen_cache["time_text"] = gui.Text(
            time_string, timefont_size, color=fontcolor, font=self.ui.basefont_file, shadowoffset=(0.5, 0.5))
        self.idlescreen_cache["time_text"].Position = self.ui.calculate_position(
            (0, 0), self.idlescreen_cache["time_text"].Surface, "center", "center")

        empty_image = pygame.Surface(
            self.ui.display_size)

        def reset_idle():
            self.is_idle = False

        self.idlescreen_cache["button"] = gui.Button(
            empty_image, self.ui.display_size, reset_idle)
        self.idlescreen_cache["button"].Position = (0, 0)

    def idlescreen(self):
        if not hasattr(self, 'idlescreen_cache'):
            self.cache_idlescreen()
        new_time = int(time.time())
        if new_time != self.old_time:
            self.old_time = new_time
            self.cache_idlescreen()
        self.ui.elements.append(self.idlescreen_cache["button"])
        self.ui.elements.append(self.idlescreen_cache["time_text"])

    def cache_clockscreen(self):
        self.clockscreen_cache = {}

        time_string = datetime.now().strftime(
            self.config.setting["timeformat"])
        timefont_size = self.ui.calculate_font_size(30)

        self.clockscreen_cache["time_text"] = gui.Text(
            time_string, timefont_size, font=self.ui.basefont_file, shadowoffset=(0.5, 0.5))
        self.clockscreen_cache["time_text"].Position = self.ui.calculate_position(
            (0, 0), self.clockscreen_cache["time_text"].Surface, "center", "center")

    def clockscreen(self):
        if not hasattr(self, 'clockscreen_cache'):
            self.cache_clockscreen()

        new_time = int(datetime.now().minute)
        if new_time != self.old_time:
            self.old_time = new_time
            self.cache_clockscreen()

        self.ui.elements.append(self.clockscreen_cache["time_text"])

        self.player_widget("play")
        self.datewidget()
        self.alarm_widget()

    def cache_alarmscreen(self):

        self.alarmscreen_cache = {}
        icon_size = (
            self.ui.display_size[0] * .3, self.ui.display_size[1] * .3)
        icon_size_enable = (
            self.ui.display_size[0] * .1, self.ui.display_size[1] * .1)

        epoch = int(time.time())
        if (epoch % 2) == 0:
            fgcolor = self.ui.bg_color
            bgcolor = self.ui.fg_color
            shadow = False
        else:
            fgcolor = self.ui.fg_color
            bgcolor = pygame.Color(0, 0, 0, 0)
            shadow = True

        self.alarmscreen_cache["background"] = gui.GuiObject()
        self.alarmscreen_cache["background"].Surface = pygame.Surface(
            self.ui.display_size, flags=pygame.SRCALPHA)
        self.alarmscreen_cache["background"].Position = (0, 0)
        self.alarmscreen_cache["background"].Surface.fill(bgcolor)

        current_time_text = str(
            datetime.now().strftime(self.config.setting["timeformat"]))

        self.alarmscreen_cache["alarm_button"] = gui.Button(
            self.ui.image_cache["alarm-snooze.png"], icon_size, self.snooze_alarm)
        self.alarmscreen_cache["alarm_button"].Position = self.ui.calculate_position(
            (0, -55), self.alarmscreen_cache["alarm_button"].Surface, "center", "center")

        self.alarmscreen_cache["alarm_disabled_button"] = gui.Button(
            self.ui.image_cache["alarm-disabled-symbolic.png"], icon_size, self.stop_alarm)
        self.alarmscreen_cache["alarm_disabled_button"].Position = self.ui.calculate_position(
            (0, -55), self.alarmscreen_cache["alarm_disabled_button"].Surface, "center", "center")

        self.alarmscreen_cache["alarm_edit_enabled_button"] = gui.Button(
            self.ui.image_cache["alarm-edit-enabled.png"], icon_size_enable, self.disable_alarm)
        self.alarmscreen_cache["alarm_edit_enabled_button"].Position = self.ui.calculate_position(
            (0, 0), self.alarmscreen_cache["alarm_edit_enabled_button"].Surface, "top", "center")

        self.alarmscreen_cache["alarm_edit_disabled_button"] = gui.Button(
            self.ui.image_cache["alarm-edit-disabled.png"], icon_size_enable, self.enable_alarm)
        self.alarmscreen_cache["alarm_edit_disabled_button"].Position = self.ui.calculate_position(
            (0, 0), self.alarmscreen_cache["alarm_edit_disabled_button"].Surface, "top", "center")

        timefont_size = self.ui.calculate_font_size(25)

        time_text = gui.Text(
            current_time_text, timefont_size, font=self.ui.boldfont_file, color=fgcolor, shadow=shadow)

        self.alarmscreen_cache["time_text_button"] = gui.Button(
            time_text.Surface, time_text.Surface.get_size(), self.stop_alarm)
        self.alarmscreen_cache["time_text_button"].Position = self.ui.calculate_position(
            (0, -30), self.alarmscreen_cache["alarm_button"].Surface, "center", "center")
        self.alarmscreen_cache["time_text_button"].Position = (
            self.alarmscreen_cache["alarm_button"].Position[0] + icon_size[1]*1.2, self.alarmscreen_cache["alarm_button"].Position[1])

    def alarmscreen(self):
        self.enable_alarm()

        if not hasattr(self, 'alarmscreen_cache'):
            self.cache_alarmscreen()

        if not self.musicplayer.playing and not self.player_primed:
            self.player_primed = True
            self.musicplayer.setAlarmPlaylist()
            self.musicplayer.play()

        new_time = int(time.time())
        if new_time != self.old_time:
            self.old_time = new_time
            self.cache_alarmscreen()

        self.ui.elements.append(self.alarmscreen_cache["background"])
        self.ui.elements.append(self.alarmscreen_cache["time_text_button"])
        if self.alarm.enabled:
            self.ui.elements.append(self.alarmscreen_cache["alarm_button"])
            self.ui.elements.append(self.alarmscreen_cache["alarm_edit_enabled_button"])
        else:
            self.ui.elements.append(self.alarmscreen_cache["alarm_disabled_button"])
            self.ui.elements.append(self.alarmscreen_cache["alarm_edit_disabled_button"])

    def cache_musicscreen(self):
        self.musicscreen_cache = {}
        self.musicplayer.trackdata_changed = False

        if self.musicplayer.image != None:
            albumart_image_size = (
                self.ui.display_size[0] * .25, self.ui.display_size[1] * .5)
            self.musicscreen_cache["albumart_image"] = gui.Image(
                self.musicplayer.image, albumart_image_size)
        else:
            self.musicscreen_cache["albumart_image"] = gui.Image(
                pygame.Surface((1, 1), flags=pygame.SRCALPHA))

        self.musicscreen_cache["albumart_image"].Position = self.ui.calculate_position(
            (0, 4), self.musicscreen_cache["albumart_image"].Surface, "center", "left")

        track = self.musicplayer.title
        trackfont_size = self.ui.calculate_font_size(4)

        self.musicscreen_cache["track_text"] = gui.Text(track, trackfont_size,
                                                        font=self.ui.boldfont_file, wrapwidth=16)
        self.musicscreen_cache["track_text"].Position = self.ui.calculate_position(
            (0, 0), self.musicscreen_cache["track_text"].Surface, "center", "left")

        self.musicscreen_cache["track_text"].Position = (self.musicscreen_cache["albumart_image"].Position[0] +
                                                         self.musicscreen_cache["albumart_image"].Surface.get_size()[0]*1.05, self.musicscreen_cache["track_text"].Position[1])

        artistfont_size = self.ui.calculate_font_size(3)
        self.musicscreen_cache["artist_text"] = gui.Text(
            self.musicplayer.artist, artistfont_size, font=self.ui.basefont_file)

        artist_text_y = self.musicscreen_cache["track_text"].Position[1] - (
            self.ui.display_size[1] * 0.08)
        self.musicscreen_cache["artist_text"].Position = (
            self.musicscreen_cache["track_text"].Position[0], artist_text_y)

        self.musicscreen_cache["album_text"] = gui.Text(self.musicplayer.album,
                                                        artistfont_size, font=self.ui.basefont_file)
        album_text_y = (
            (self.ui.display_size[1] * 0.03) + self.musicscreen_cache["track_text"].Rect.bottom)
        self.musicscreen_cache["album_text"].Position = (
            self.musicscreen_cache["track_text"].Position[0], album_text_y)

    def musicscreen(self):
        if not hasattr(self, 'musicscreen_cache') or self.musicplayer.trackdata_changed:
            self.cache_musicscreen()

        self.player_widget()
        self.datewidget(True)
        self.alarm_widget()
        self.ui.elements.append(self.musicscreen_cache["albumart_image"])
        self.ui.elements.append(self.musicscreen_cache["artist_text"])
        self.ui.elements.append(self.musicscreen_cache["track_text"])
        self.ui.elements.append(self.musicscreen_cache["album_text"])

    def cache_player_widget(self):
        self.player_widget_cache = {}
        icon_size = (
            self.ui.display_size[0] * .15, self.ui.display_size[1] * .15)
        panel_size = (
            self.ui.display_size[0], self.ui.display_size[1] * .15)
        self.player_widget_cache["panel"] = gui.GuiObject()
        self.player_widget_cache["panel"].Surface = pygame.Surface(
            panel_size, flags=pygame.SRCALPHA)
        self.player_widget_cache["panel"].Position = self.ui.calculate_position(
            (0, 0), self.player_widget_cache["panel"].Surface, "bottom", "left")
        gui.fill_gradient(self.player_widget_cache["panel"].Surface, pygame.Color(
            0, 0, 0, 0), pygame.Color(0, 0, 0, 255), vertical=True)

        self.player_widget_cache["play_button"] = gui.Button(
            self.ui.image_cache["play.png"], icon_size, self.musicplayer.togglePlay)
        self.player_widget_cache["pause_button"] = gui.Button(
            self.ui.image_cache["pause.png"], icon_size, self.musicplayer.togglePlay)
        self.player_widget_cache["play_button"].Position = self.player_widget_cache["pause_button"].Position = self.ui.calculate_position(
            (0, -18), self.player_widget_cache["play_button"].Surface, "bottom", "right")

        self.player_widget_cache["sf_button"] = gui.Button(
            self.ui.image_cache["sf.png"], icon_size, self.musicplayer.skip)
        self.player_widget_cache["sf_button"].Position = (
            self.player_widget_cache["play_button"].Position[0] + icon_size[1], self.player_widget_cache["play_button"].Position[1])

        self.player_widget_cache["sb_button"] = gui.Button(
            self.ui.image_cache["sb.png"], icon_size, self.musicplayer.back)
        self.player_widget_cache["sb_button"].Position = (
            self.player_widget_cache["play_button"].Position[0] - icon_size[1], self.player_widget_cache["play_button"].Position[1])

        self.player_widget_cache["volup_button"] = gui.Button(
            self.ui.image_cache["volup.png"], icon_size, self.musicplayer.volup)
        self.player_widget_cache["volup_button"].Position = self.ui.calculate_position(
            (0, 32), self.player_widget_cache["play_button"].Surface, "bottom", "left")

        self.player_widget_cache["volmute"] = gui.Button(
            self.ui.image_cache["volmute.png"], icon_size, self.musicplayer.toggleMute)
        self.player_widget_cache["vollow"] = gui.Button(
            self.ui.image_cache["vollow.png"], icon_size, self.musicplayer.toggleMute)
        self.player_widget_cache["volmed"] = gui.Button(
            self.ui.image_cache["volmed.png"], icon_size, self.musicplayer.toggleMute)
        self.player_widget_cache["volhigh"] = gui.Button(
            self.ui.image_cache["volhigh.png"], icon_size, self.musicplayer.toggleMute)

        self.player_widget_cache["volmute"].Position = self.player_widget_cache["volhigh"].Position = self.player_widget_cache["volmed"].Position = self.player_widget_cache["vollow"].Position = (
            self.player_widget_cache["volup_button"].Position[0] - icon_size[1], self.player_widget_cache["volup_button"].Position[1])

        self.player_widget_cache["voldown_button"] = gui.Button(
            self.ui.image_cache["voldown.png"], icon_size, self.musicplayer.voldown)
        self.player_widget_cache["voldown_button"].Position = (
            self.player_widget_cache["volmute"].Position[0] - icon_size[1], self.player_widget_cache["volmute"].Position[1])

    def player_widget(self, style=""):
        if not hasattr(self, 'player_widget_cache'):
            self.cache_player_widget()

        if self.musicplayer.playing:
            icon = "pause_button"
        else:
            icon = "play_button"

        self.ui.elements.append(self.player_widget_cache["panel"])
        self.ui.elements.append(self.player_widget_cache[icon])

        if style != "play":

            if self.musicplayer.muted:
                volume_icon = "volmute"
            elif self.musicplayer.volume < 34:
                volume_icon = "vollow"
            elif self.musicplayer.volume < 66:
                volume_icon = "volmed"
            else:
                volume_icon = "volhigh"

            self.ui.elements.append(self.player_widget_cache["sf_button"])
            self.ui.elements.append(self.player_widget_cache["sb_button"])

            self.ui.elements.append(self.player_widget_cache["volup_button"])
            self.ui.elements.append(self.player_widget_cache["voldown_button"])
            self.ui.elements.append(self.player_widget_cache[volume_icon])

    def switch_to_defaultscreen(self, reset=False):
        if self.alarm.alarm_active:
            self.is_idle = False
            self.current_screen = self.alarmscreen
            return

        if self.is_idle and self.current_screen != self.musicscreen and self.current_screen != self.alarmscreen:
            self.ui.redraw = True
            self.current_screen = self.idlescreen
            return

        if self.current_screen != self.alarmset_screen or reset:
            if self.alarm.alarm_active:
                self.ui.redraw = True
                self.current_screen = self.alarmscreen
            elif self.musicplayer.playing:
                self.ui.redraw = True
                self.current_screen = self.musicscreen
            else:
                self.ui.redraw = True
                self.current_screen = self.clockscreen

    def cache_datewidget(self):
        self.datewidget_cache = {}
        datefont_size = self.ui.calculate_font_size(4)

        datetime_text = (datetime.now().strftime(
            self.config.setting["dateformat"]) + "  " + datetime.now().strftime(self.config.setting["timeformat"])).upper()
        self.datetime_text = datetime_text

        date_text = datetime.now().strftime(
            self.config.setting["dateformat"]).upper()

        self.datewidget_cache["datetime_text"] = gui.Text(
            datetime_text, datefont_size, self.ui.boldfont_file)

        self.datewidget_cache["date_text"] = gui.Text(
            date_text, datefont_size, self.ui.boldfont_file)

        self.datewidget_cache["datetime_text"].Position = self.ui.calculate_position(
            (1, -3), self.datewidget_cache["datetime_text"].Surface, "top", "right")
        self.datewidget_cache["date_text"].Position = self.ui.calculate_position(
            (1, -3), self.datewidget_cache["date_text"].Surface, "top", "right")

    def datewidget(self, time=False):
        datetime_text = (datetime.now().strftime(
            self.config.setting["dateformat"]) + "  " + datetime.now().strftime(self.config.setting["timeformat"])).upper()
        if not hasattr(self, 'datewidget_cache') or self.datetime_text != datetime_text:
            self.cache_datewidget()

        if time:
            self.ui.elements.append(self.datewidget_cache["datetime_text"])
        else:
            self.ui.elements.append(self.datewidget_cache["date_text"])

    def switch_to_alarmset_screen(self):
        self.current_screen = self.alarmset_screen
        self.ui.redraw = True

    def cache_alarm_widget(self, updatetime=False):
        icon_size = (
            self.ui.display_size[0] * .05, self.ui.display_size[1] * .05)
        icon_size_enable = (
            self.ui.display_size[0] * .1, self.ui.display_size[1] * .1)
        if not updatetime:
            self.alarm_widget_cache = {}
            self.alarm_widget_cache["alarm_image_button"] = gui.Button(self.ui.image_cache[
                "alarm-symbolic.png"], icon_size, self.switch_to_alarmset_screen)
            self.alarm_widget_cache["alarm_image_button"].Position = self.ui.calculate_position(
                (1, 4), self.alarm_widget_cache["alarm_image_button"].Surface, "top", "left")

            self.alarm_widget_cache["alarm_image_disabled_button"] = gui.Button(self.ui.image_cache[
                "alarm-disabled-symbolic.png"], icon_size, self.switch_to_alarmset_screen)
            self.alarm_widget_cache["alarm_image_disabled_button"].Position = self.ui.calculate_position(
                (1, 4), self.alarm_widget_cache["alarm_image_disabled_button"].Surface, "top", "left")

            self.alarm_widget_cache["alarm_snooze_button"] = gui.Button(self.ui.image_cache[
                "alarm-snooze.png"], icon_size, self.alarm.turnOffSnooze)
            self.alarm_widget_cache["alarm_snooze_button"].Position = self.ui.calculate_position(
                (1, 4), self.alarm_widget_cache["alarm_snooze_button"].Surface, "top", "left")

        self.alarm_widget_cache["time"] = str(self.alarm.alarmtime.strftime(
            self.config.setting["timeformat"])).upper()
        alarmfont_size = self.ui.calculate_font_size(4.5)
        alarm_text = gui.Text(
            self.alarm_widget_cache["time"], alarmfont_size, self.ui.boldfont_file)
        self.alarm_widget_cache["alarm_text_button"] = gui.Button(
            alarm_text.Surface, alarm_text.Surface.get_size(), self.switch_to_alarmset_screen)
        self.alarm_widget_cache["alarm_text_button"].Position = (
            self.alarm_widget_cache["alarm_image_button"].Position[0] + (icon_size[1]*1.1) + 20, self.alarm_widget_cache["alarm_image_button"].Position[1]*1.2)

        self.alarm_widget_cache["alarm_edit_enabled_button"] = gui.Button(
            self.ui.image_cache["alarm-edit-enabled.png"], icon_size_enable, self.disable_alarm)
        self.alarm_widget_cache["alarm_edit_enabled_button"].Position = self.ui.calculate_position(
            (0, 0), self.alarm_widget_cache["alarm_edit_enabled_button"].Surface, "top", "center")

        self.alarm_widget_cache["alarm_edit_disabled_button"] = gui.Button(
            self.ui.image_cache["alarm-edit-disabled.png"], icon_size_enable, self.enable_alarm)
        self.alarm_widget_cache["alarm_edit_disabled_button"].Position = self.ui.calculate_position(
            (0, 0), self.alarm_widget_cache["alarm_edit_disabled_button"].Surface, "top", "center")

    def alarm_widget(self):
        if not hasattr(self, 'alarm_widget_cache'):
            self.cache_alarm_widget()

        current_time_text = str(self.alarm.alarmtime.strftime(
            self.config.setting["timeformat"])).upper()

        if self.alarm_widget_cache["time"] != current_time_text:
            self.cache_alarm_widget(updatetime=True)

        self.ui.elements.append(self.alarm_widget_cache["alarm_text_button"])
        if self.alarm.snooze and not self.alarm.alarm_active:
            self.ui.elements.append(self.alarm_widget_cache["alarm_snooze_button"])
            self.ui.elements.append(self.alarm_widget_cache["alarm_edit_enabled_button"])
        elif self.alarm.enabled:
            self.ui.elements.append(self.alarm_widget_cache["alarm_image_button"])
            self.ui.elements.append(self.alarm_widget_cache["alarm_edit_enabled_button"])
        else:
            self.ui.elements.append(self.alarm_widget_cache["alarm_image_disabled_button"])
            self.ui.elements.append(self.alarm_widget_cache["alarm_edit_disabled_button"])

    def cache_alarmset_screen(self):
        self.alarmset_screen_cache = {}

        def changeAlarmTime(m):
            delattr(self, 'alarmset_screen_cache')
            self.alarm.changeAlarm(m)

        alarmtime_text = self.alarm.time.strftime(
            self.config.setting["timeformat"])
        alarmtime_size = self.ui.calculate_font_size(22)
        self.alarmset_screen_cache["alarmtime"] = gui.Text(
            alarmtime_text, alarmtime_size, self.ui.boldfont_file, shadowoffset=(0.5, 0.5))
        self.alarmset_screen_cache["alarmtime"].Position = self.ui.calculate_position(
            (0, -14), self.alarmset_screen_cache["alarmtime"].Surface, "center", "right")

        icon_size = (
            self.ui.display_size[0] * .25, self.ui.display_size[1] * .25)

        big_icon_size = (
            self.ui.display_size[0] * .33, self.ui.display_size[1] * .33)

        self.alarmset_screen_cache["addminute_button"] = gui.Button(
            self.ui.image_cache["add.png"], icon_size, lambda: changeAlarmTime(1), lambda: changeAlarmTime(5))
        self.alarmset_screen_cache["addminute_button"].Position = self.ui.calculate_position(
            (-15, -20), self.alarmset_screen_cache["addminute_button"].Surface, "center", "right")

        self.alarmset_screen_cache["subminute_button"] = gui.Button(
            self.ui.image_cache["sub.png"], icon_size, lambda: changeAlarmTime(-1), lambda: changeAlarmTime(-5))
        self.alarmset_screen_cache["subminute_button"].Position = self.ui.calculate_position(
            (15, -20), self.alarmset_screen_cache["subminute_button"].Surface, "center", "right")

        self.alarmset_screen_cache["addhour_button"] = gui.Button(
            self.ui.image_cache["add.png"], icon_size, lambda: changeAlarmTime(60))
        self.alarmset_screen_cache["addhour_button"].Position = self.ui.calculate_position(
            (-15, -65), self.alarmset_screen_cache["addhour_button"].Surface, "center", "right")

        self.alarmset_screen_cache["subhour_button"] = gui.Button(
            self.ui.image_cache["sub.png"], icon_size, lambda: changeAlarmTime(-60))
        self.alarmset_screen_cache["subhour_button"].Position = self.ui.calculate_position(
            (15, -65), self.alarmset_screen_cache["subhour_button"].Surface, "center", "right")

        self.alarmset_screen_cache["cancel_button"] = gui.Button(
            self.ui.image_cache["cancel.png"], big_icon_size, self.reset_alarm)
        self.alarmset_screen_cache["cancel_button"].Position = self.ui.calculate_position(
            (-15, 25), self.alarmset_screen_cache["cancel_button"].Surface, "center", "left")

        self.alarmset_screen_cache["ok_button"] = gui.Button(
            self.ui.image_cache["ok.png"], big_icon_size, self.set_alarm)
        self.alarmset_screen_cache["ok_button"].Position = self.ui.calculate_position(
            (15, 25), self.alarmset_screen_cache["ok_button"].Surface, "center", "left")

    def alarmset_screen(self):
        if not hasattr(self, 'alarmset_screen_cache'):
            self.cache_alarmset_screen()
        self.ui.redraw = True

        self.ui.elements.append(self.alarmset_screen_cache["alarmtime"])

        self.ui.elements.append(self.alarmset_screen_cache["addminute_button"])
        self.ui.elements.append(self.alarmset_screen_cache["subminute_button"])
        self.ui.elements.append(self.alarmset_screen_cache["addhour_button"])
        self.ui.elements.append(self.alarmset_screen_cache["subhour_button"])

        self.ui.elements.append(self.alarmset_screen_cache["ok_button"])
        self.ui.elements.append(self.alarmset_screen_cache["cancel_button"])

    def set_alarm(self):
        self.alarm.setAlarm()
        self.config.setting["alarmtime"] = self.alarm.alarmtime.strftime("%H:%M")
        self.config.save()
        self.switch_to_defaultscreen(True)

    def reset_alarm(self):
        self.alarm.resetAlarm()
        self.switch_to_defaultscreen(True)

    def stop_alarm(self):
        self.alarm.alarm_active = False
        self.player_primed = False
        self.current_screen = self.clockscreen
        self.ui.redraw = True

    def snooze_alarm(self):
        self.alarm.alarm_active = False
        self.player_primed = False
        self.current_screen = self.clockscreen
        self.alarm.turnOnSnooze()
        self.ui.redraw = True

    def disable_alarm(self):
        self.alarm.disableAlarm()
        self.alarm.alarm_active = False
        self.player_primed = False
        self.current_screen = self.clockscreen
        self.alarm.turnOffSnooze()
        self.config.setting["enabled"] = "0"
        self.config.save()
        self.ui.redraw = True

    def enable_alarm(self):
        self.alarm.enableAlarm()
        self.current_screen = self.clockscreen
        self.config.setting["enabled"] = "1"
        self.config.save()
        self.ui.redraw = True

    def alarm_triggered(self):
        self.current_screen == self.alarmscreen
        self.alarm.alarm_active = True
        self.ui.redraw = True
        self.musicplayer.setAlarmPlaylist()
        if not self.musicplayer.playing:
            self.musicplayer.play()

    # the main loop
    def loop(self):
        while True:
            self.ui.elements.clear()
            self.switch_to_defaultscreen()
            if self.current_screen != None:
                self.current_screen()

            self.ui.update()


if __name__ == "__main__":
    app = application()
