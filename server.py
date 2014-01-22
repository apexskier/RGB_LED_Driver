import json
from bottle import redirect, request, route, run, template, get, post, static_file
from bottle.ext.websocket import GeventWebSocketServer
from bottle.ext.websocket import websocket
from rgbDriver import RGBDriver, SingleLEDDriver

rgb_driver = RGBDriver()
simple_driver = SingleLEDDriver()

@get('/')
def index():
    return template('index')

@get('/control', apply=[websocket])
def do_color(ws):
    while True:
        message = ws.receive()
        if message:
            print "Recieved message: " + message
            data = json.loads(message)
            if data[u'action'] == 'color':
                rgb_driver.set_hex_color(data[u'value'])
            elif data[u'action'] == 'set_simple':
                simple_driver.set_l(data[u'value'])
        else:
            break

@route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root='static')

run(host='0.0.0.0', port=8080, server=GeventWebSocketServer)
