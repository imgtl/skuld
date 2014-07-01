#!/usr/bin/env python

import subprocess
import requests
import simplejson

from flask import Flask, request
from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM

class skuld(Thread):
    def __init__(self):
        self.S = socket(AF_INET, SOCK_STREAM)
        Thread.__init__(self)

    def run(self):
        self.S.connect(('10.54.45.100', 6667))
        self.F = self.S.makefile()
        self.send_raw_line('NICK skuld')
        self.send_raw_line('USER skuld 8 * :skuld')

        while 1:
            line = self.F.readline().strip()
            if line == '':
                break
            print '>>> %s' % line
            token = line.split(' ')
            if token[0] == 'PING':
                self.send_raw_line('PONG %s' % token[1])
            elif token[1] == '001':
                self.on_welcome()

    def send_raw_line(self, line):
        self.S.send("%s\r\n" % line)
        print '<<< %s' % line

    def send_message(self, line):
        self.send_raw_line('PRIVMSG #channel : %s' % line)

    def on_welcome(self):
        self.send_raw_line('JOIN #channel')


app = Flask(__name__)
app.config['SECRET_KEY'] = '(secret key here)'

@app.route('/travis', methods=['POST'])
def travis():
    payload = request.form.get('payload')
    json = simplejson.loads(payload)
    print(payload)
    if json['status'] == 0:
        skuld.send_message('[imgtl] CI Build #%s success. Starting pull-and-apply jobs' % json['number'])
        subprocess.call(['/root/update.sh'])
        skuld.send_message('[imgtl] Change has been successfully deployed into the production server')
        r = requests.head('https://img.tl/')
        if r.status_code != 200:
            skuld.send_message('[imgtl] WARNING! imgtl returns %d. is something wrong?' % r.status_code)
        r = requests.head('https://api.img.tl/')
        if r.status_code != 200:
            skuld.send_message('[imgtl] WARNING! imgtl.api returns %d. is something wrong?' % r.status_code)
    elif json['status_message'] == 'Pending':
        skuld.send_message('[imgtl] CI Build #%s was started on travis. to check out: %s' % (json['number'], json['build_url']))
    elif json['status_message'] == 'Errored':
        skuld.send_message('[imgtl] CI Build #%s was \002errored\x0f. to check out: %s' % (json['number'], json['build_url']))
    elif json['status_message'] == 'Failed' or json['status_message'] == 'Still Failing':
        skuld.send_message('[imgtl] CI Build #%s was \002failed\x0f. to check out: %s' % (json['number'], json['build_url']))
    return ''

if __name__ == '__main__':
    skuld = skuld()
    skuld.daemon = True
    skuld.start()

    app.run(host='127.0.0.1', port=2562, debug=False)
