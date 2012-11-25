#!/usr/bin/env python

''' Wrapper script which redirects your command's
STDOUT and STDERR to a log file and then makes
it available via a Flask web application so that 
you can see its output/monitor it while away

Amit Saha.

'''
import optparse
import subprocess
import sys
import os
import socket

from flask import Flask, Response

app = Flask(__name__)

def getip():
    ''' Get the public facing IP address'''
    
    # Recipe: http://stackoverflow.com/a/166589/59634

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("gmail.com",80))
    ipaddr = s.getsockname()[0]
    s.close()
        
    return ipaddr

@app.route('/<path:logfile>')
def sendlog(logfile):
    if os.path.exists(os.path.abspath('/tmp/'+logfile)):
        lines = ''
        with open(os.path.abspath('/tmp/'+logfile),'r') as f:
            for line in f:
                lines = lines + line
        return Response(lines,mimetype='text')
    else:
        return Response('Error. No Such Log file',mimetype='text')

@app.route('/')
def index():
    return "You should not have been here"

def start_server():

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:                         
        s.connect(('localhost', 5100))
    except:
        if os.fork()==0:
            app.run('0.0.0.0', port = 5100)
        else:
            return
    else:
        return
  
def start_process(process):
    fname='/tmp/{0}.log'.format(process.split()[0])
    f=open(fname,'w')
    subprocess.Popen(list(process.split()),stdout=f,\
                         stderr=subprocess.STDOUT)
    return os.path.abspath(fname)

if __name__=='__main__':
    # setup options
    parser = optparse.OptionParser()
    parser.add_option('-p', '--process',
                      help='Process name with options/switches',
                      dest='process')

    #parse
    (opts, args) = parser.parse_args()
    
    if opts.process is None:
        parser.print_help()
        sys.exit(-1)
    
    # start the process
    log=start_process(opts.process)
    # serve STDOUT and STDERR
    start_server()
    print 'Your log is now available at:: {0}:5100/{1}'.\
        format(getip(),os.path.split(log)[1])

