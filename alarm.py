from datetime import datetime, timedelta
import time
import threading


class Alarm(object):
    enabled = False
    alarm_active = False
    old_time = 0

    def __init__(self, alarmtime):
        self.alarmtime = datetime.strptime(alarmtime, "%H:%M")
        self.time = self.alarmtime
        self.check_alarm_thread = threading.Thread(target=self.check_alarm)
        self.check_alarm_thread.daemon = True
        self.check_alarm_thread.start()

    def check_alarm(self):
        while True:
            new_time = int(datetime.now().minute)
            if new_time != self.old_time:
                self.old_time = new_time
                if self.alarmtime.hour == datetime.now().hour and self.alarmtime.minute == datetime.now().minute:
                    self.alarm_active = True
            time.sleep(1)

    def setAlarm(self):
        self.alarmtime = self.time

    def resetAlarm(self):
        self.time = self.alarmtime

    def changeAlarm(self, m):
        self.time += timedelta(minutes=m)
