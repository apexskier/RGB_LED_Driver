import json
from bottle import redirect, request, route, run, template, get, post, static_file
from bottle.ext.websocket import GeventWebSocketServer
from bottle.ext.websocket import websocket
from rgbDriver import RGBDriver, SingleLEDDriver

targets = {
        'rgb1': RGBDriver(0, 1, 2),
        'led1': SingleLEDDriver(3)
    }

@get('/')
def index():
    return template('index')

@get('/control', apply=[websocket])
def control(ws):
    while True:
        message = ws.receive()
        if message:
            print "Recieved message: " + message
            data = json.loads(message)
            driver = None
            if u'target' in data:
                driver = targets[str(data[u'target'])]
                driver_type = type(driver)
                action = data[u'action']
                if action == 'set':
                    if driver_type == RGBDriver:
                        driver.set_hex_color(data[u'value'])
                    elif driver_type == SingleLEDDriver:
                        driver.set_l(data[u'value'])
                if action == 'off':
                    driver.to_off()

        else:
            break

@route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root='static')

run(host='0.0.0.0', port=8080, server=GeventWebSocketServer)
