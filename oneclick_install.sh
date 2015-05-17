#!/bin/bash
python3 -m venv venv --without-pip
source venv/bin/activate
wget https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py
rehash
ln -s /usr/bin/python2.7 venv/bin/python2.7
source venv/bin/activate
pip3 install -r requirements.txt
wget scapy.net -O scapy-latest.zip
unzip scapy-latest.zip
cd scapy-2.*
sudo ../venv/bin/python2.7 setup.py install
cd ..
git clone https://github.com/alice1992224/sniff_web.git