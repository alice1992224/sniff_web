#!/bin/bash
sudo apt-get update
sudo apt-get install git
git clone https://github.com/alice1992224/sniff_web.git
cd sniff_web
source venv/bin/activate
ip=`ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1'`
sudo ./venv/bin/python3 manage.py runserver $ip:7778