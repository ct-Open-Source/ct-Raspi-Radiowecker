
# Einrichtung des Raspi-Radioweckers

## Paketinstallation

```
wget -q -O - https://apt.mopidy.com/mopidy.gpg | sudo apt-key add -

sudo wget -q -O /etc/apt/sources.list.d/mopidy.list https://apt.mopidy.com/buster.list

sudo apt update && sudo apt upgrade

sudo apt install --no-install-recommends xserver-xorg xinit xterm xserver-xorg-input-evdev xserver-xorg-video-fbturbo lightdm gstreamer1.0-alsa python3-pip python3-pygame python3-venv python3-wheel python-pip python-setuptools python-wheel python-alsaaudio mopidy mopidy-tunein mopidy-podcast-itunes 
```

## Displayeinrichtung

```
wget https://github.com/waveshare/LCD-show/archive/master.zip

unzip master.zip

cd LCD-Show-master

sudo ./LCD5-show
```

## Mopidy-Addons nachinstallieren

```
sudo python3 -m pip install Mopidy-Mobile Mopidy-ALSAMixer 
```

## Python-Umgebung für das Touch-Interface einrichten

```
python3 -m venv ~/venv

source ~/venv/bin/activate

pip install -r ~/alarm/requirements.txt
```

## Shell-Skript ausführbar machen

```
chmod +x ~/alarm/run.sh
```
