#!/bin/bash
cd /imgtl
sudo -u imgtl git pull
pip install --upgrade -r requirements.txt
scss --style compressed --update static/scss:static/css
service uwsgi restart
