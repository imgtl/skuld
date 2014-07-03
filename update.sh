#!/bin/bash
cd /imgtl
sudo -u imgtl git pull
sudo -u imgtl scss --style compressed --update static/scss:static/css
pip install --upgrade -r requirements.txt
service uwsgi restart
