#!/bin/bash
# This script install dependancies for the markov keyboard and the flask web server

thisScriptDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
pythonPath=$(which python3)

echo "
------------installing dependencies :------------
"
echo "
updating the system :"
sudo apt-get update||exit 1
sudo apt-get -y dist-upgrade||exit 1
echo "
installing .deb packages :"
sudo apt-get -y --fix-missing install python3-pip python3-dev zip libasound2-dev unclutter libatlas-base-dev libjack-jackd2-dev||exit 1
echo "
installing pip packages :"
pip3 install numpy ||exit 2
pip3 install mchmm ||exit 2
pip3 install flask ||exit 2
pip3 install flask-socketio||exit 2
#~ pip3 install flask-uploads||exit 2
#~ pip3 install Cython||exit 2
pip3 install python-rtmidi||exit 2
pip3 install mido||exit 2
pip3 install eventlet||exit 2
pip3 install pynput||exit 2

echo "
------------DONE installing dependencies------------
"

echo"
------ setting up the hostname as IA-keyboard ------"
sudo raspi-config nonint do_hostname "IA-keyboard"
echo"
--------- setting up the wifi country as FR---------"
sudo raspi-config nonint do_wifi_country FR

echo "
---------- configuring browser auto-start: ---------

"
sudo touch /etc/xdg/lxsession/LXDE-pi/autostart
sudo echo "
# Auto run the browser
@xset s off
@xset -dpms
@xset s noblank
@unclutter -idle 0
@$pythonPath /home/pi/keyboard/main.py > /home/pi/keyboard/keyboard`date +%d%m%y%H%M`.log
@chromium-browser --kiosk $thisScriptDir/templates/loading.html
">>/etc/xdg/lxsession/LXDE-pi/autostart # for raspbian buster
#~/.config/lxsession/LXDE-pi/autostart for raspbian stretch
echo "
--------------- disabling sleep mode ---------------
"
sudo echo"
xserver-command=X -s 0 dpms
">>/etc/lightdm/lightdm.conf

#~ echo "
#~ ----------- setting up the access point ------------
#~ "
#~ chmod +x STAtoAP
#~ sudo ./STAtoAP

echo "

----------------------------------------------------
----------- DONE, rebooting in 3, 2, 1... ----------
----------------------------------------------------"
sleep(3); sudo reboot
