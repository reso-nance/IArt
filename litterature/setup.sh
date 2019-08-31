#!/bin/bash
# This script install dependancies for the markov keyboard and the flask web server

echo "
------------installing dependencies :------------
"
echo "
updating the system :"
sudo apt-get update||exit 1
sudo apt-get -y dist-upgrade||exit 1
echo "
installing .deb packages :"
sudo apt-get -y --fix-missing install python3-pip python3-dev python3-serial||exit 1
echo "
installing pip packages :"
pip3 install flask ||exit 2
pip3 install flask-socketio||exit 2
pip3 install eventlet||exit 2
pip3 install markovify||exit 2
pip3 install spacy||exit 2
python -m spacy download fr_core_news_sm||exit 2
#~ pip3 install flask-uploads||exit 2
#~ pip3 install Cython||exit 2

echo "
------------DONE installing dependencies------------
"
