#!/usr/bin/python
# -*- coding: utf-8 -*-
import configparser


class config:
    def __init__(self):
        self._parser = configparser.RawConfigParser()
        self.setting = ""
        self._load_config()

    def _load_config(self):
        try:
            # load the configuration file and load the nettester segment
            self._parser.read('clock.conf')
            if "clock" in self._parser:
                self.setting = self._parser['clock']
        except Exception as exc:
            # return the error and exit
            print("Loading the configuration file failed")
            print(exc)
            exit()

    def save(self):
        with open('clock.conf', 'w+') as configfile:
            writer = configparser.RawConfigParser()
            writer.add_section('clock')
            for key in self.setting.keys():
                writer.set('clock', key, self.setting[key])
            writer.write(configfile)
            configfile.close()
