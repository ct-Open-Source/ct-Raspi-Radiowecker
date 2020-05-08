#!/bin/bash
source ~/venv/bin/activate
cd ~/alarm
while true; do
python ct-alarm-radio.py
sleep 30
done
