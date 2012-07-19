# modified version of: http://blog.pythonisito.com/2011/07/gevent-zeromq-websockets-and-flot-ftw.html
import os
#import time
#import math
#import json

import paste.urlparser 
import gevent
from gevent_zeromq import zmq
from geventwebsocket.handler import WebSocketHandler

def main():
    '''Set up zmq context and greenlets for all the servers, then launch the web
    browser and run the data producer'''
    context = zmq.Context()

    # zeromq: tcp to inproc gateway
    gevent.spawn(zmq_server, context)
    # websocket server: copies inproc zmq messages to websocket
    ws_server = gevent.pywsgi.WSGIServer(
        ('', 9999), WebSocketApp(context),
        handler_class=WebSocketHandler)
    # http server: serves up static files
    http_server = gevent.pywsgi.WSGIServer(
        ('', 8000),
        paste.urlparser.StaticURLParser(os.path.dirname(__file__)))
    # Start the server greenlets
    http_server.start()
    ws_server.serve_forever()
    
def zmq_server(context):
    '''Funnel messages coming from the external tcp socket to an inproc socket'''
    sock_incoming = context.socket(zmq.SUB)
    sock_outgoing = context.socket(zmq.PUB)
    sock_incoming.bind('inproc://in_chat')
    sock_outgoing.bind('inproc://queue')
    sock_incoming.setsocopt(zmq.SUBSCRIBE, "")
    while True:
        msg = sock_incoming.recv()
        sock_outgoing.send(msg)
        #x = time.time() * 1000
        #y = 2.5 * (1 + math.sin(x / 500))
        #sock_outgoing.send(json.dumps(dict(x=x, y=y)))
        #gevent.sleep(0.05)

class WebSocketApp(object):
    '''Funnel messages coming from an inproc zmq socket to the websocket'''

    def __init__(self, context):
        self.context = context

    def __call__(self, environ, start_response):
        ws = environ['wsgi.websocket']
        sock = self.context.socket(zmq.SUB)
        sock.setsockopt(zmq.SUBSCRIBE, "")
        sock.connect('inproc://queue')
        while True:
            msg = sock.recv()
            #msg = ws.receive()
            ws.send(msg)


def chat_reader(context, ws):
    socket = context.socket(zmq.PUB)
    socket.connect('inproc://in_chat')

    while True:
        msg = ws.receive()
        socket.send(msg)

if __name__ == '__main__':
    main()
