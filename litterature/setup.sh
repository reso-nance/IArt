#!/bin/bash
# This script install dependancies for the markov text generator and the flask web server

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
sudo apt-get -y --fix-missing install python3-pip python3-dev liblo-dev python3-serial unclutter||exit 1
echo "
installing pip packages :"
pip3 install flask ||exit 2
pip3 install flask-socketio||exit 2
pip3 install Cython||exit 2
pip3 install pyliblo ||exit 2
#~ pip3 install eventlet||exit 2
pip3 install markovify||exit 2
pip3 install spacy==2.0.18||exit 2 # newer versions depends on blis which is currently broken for ARM plateforms
python3 -m spacy download fr_core_news_sm||exit 2
#~ pip3 install flask-uploads||exit 2
#~ pip3 install Cython||exit 2

echo "
adding Debian non-free repository"
get -q https://ftp-master.debian.org/keys/release-10.asc -O- | sudo apt-key add -
echo "deb http://deb.debian.org/debian buster non-free" | sudo tee -a /etc/apt/sources.list
sudo apt-get update
echo "
installing picoTTS"
sudo apt-get install -y --fix-missing libttspico-utils


echo "
------------DONE installing dependencies------------

---------- configuring browser auto-start: ---------

"
sudo touch /etc/xdg/lxsession/LXDE-pi/autostart
sudo echo "
# Auto run the browser
@xset s off
@xset -dpms
@xset s noblank
@unclutter -idle 0
@$pythonPath /home/pi/litterature/main.py > /home/pi/litterature/litterature`date +%d%m%y%H%M`.log
@chromium-browser --kiosk $thisScriptDir/templates/loading.html
">>/etc/xdg/lxsession/LXDE-pi/autostart # for raspbian buster
#~/.config/lxsession/LXDE-pi/autostart for raspbian stretch
echo "
--------------- disabling sleep mode ---------------
"
sudo echo"
xserver-command=X -s 0 dpms
">>/etc/lightdm/lightdm.conf

echo"
--------- setting up the wifi country as FR---------"
sudo raspi-config nonint do_wifi_country FR

echo "
----------- setting up the access point ------------
"
chmod +x STAtoAP
sudo ./STAtoAP

echo "

----------------------------------------------------
----------- DONE, rebooting in 3, 2, 1... ----------
----------------------------------------------------"
sleep(3); sudo reboot
