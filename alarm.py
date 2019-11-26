from datetime import datetime, timedelta
import time
import threading


class Alarm(object):
    enabled = False
    alarm_active = False
    old_time = 0
    old_snooze_time = 0
    snooze = False
    snooze_timer = 0

    def __init__(self, alarmtime, snooze_for_n_seconds, musicplayer):
        self.alarmtime = datetime.strptime(alarmtime, "%H:%M")
        self.time = self.alarmtime
        self.snooze_n_seconds = int(snooze_for_n_seconds)
        self.musicplayer = musicplayer
        self.check_alarm_thread = threading.Thread(target=self.checkAlarm)
        self.check_alarm_thread.daemon = True
        self.check_alarm_thread.start()
        self.check_snooze_thread = threading.Thread(target=self.checkSnooze)
        self.check_snooze_thread.daemon = True
        self.check_snooze_thread.start()

    def checkAlarm(self):
        while True:
            new_time = int(datetime.now().minute)
            if new_time != self.old_time:
                self.old_time = new_time
                if self.enabled is True and self.alarmtime.hour == datetime.now().hour and self.alarmtime.minute == datetime.now().minute:
                    self.alarm_active = True
            time.sleep(1)

    def setAlarm(self):
        self.alarmtime = self.time

    def resetAlarm(self):
        self.time = self.alarmtime

    def changeAlarm(self, m):
        self.time += timedelta(minutes=m)

    def enableAlarm(self):
        self.enabled = True

    def disableAlarm(self):
        self.enabled = False

    def checkSnooze(self):
        while True:
            new_snooze_time = int(datetime.timestamp(datetime.now()))
            if self.enabled is True and self.snooze is True and new_snooze_time != self.old_snooze_time:
                if self.old_snooze_time == 0:
                    self.old_snooze_time = new_snooze_time
                diff = new_snooze_time - self.old_snooze_time
                self.old_snooze_time = new_snooze_time
                self.snooze_timer = self.snooze_timer - diff
                if self.snooze_timer <= 0:
                    self.snooze = False
                    self.alarm_active = True
                    self.musicplayer.togglePlay()
                    self.old_snooze_time = 0
            time.sleep(1)

    def turnOnSnooze(self):
        self.old_snooze_time = 0
        self.snooze_timer = self.snooze_n_seconds
        self.musicplayer.togglePlay()
        self.snooze = True

    def turnOffSnooze(self):
        self.snooze = False
