from bottle import redirect, request, route, run, template, get, post, static_file
from rgbDriver import RGBDriver
from pprint import pprint

rgb_driver = RGBDriver()

@get('/')
def index():
    return '''
        <link rel="stylesheet" href="/static/farbtastic/farbtastic.css"></link>
        <form action="/color" method="post">
            Color: <input name="color" id="color" type="text" value="#123456">
        </form>
        <div id="colorpicker"></div>
        <script src="/static/jquery-2.0.3.min.js"></script>
        <script src="/static/farbtastic/farbtastic.js"></script>

        <script type="text/javascript">
            $(document).ready(function() {
                $('#colorpicker').farbtastic(function(c) {
                    $('#color').val(c);
                    $.post("/color", { color: c });
                });
            });
        </script>
    '''

@post('/color')
def do_color():
    color = "#" + request.body.read()[9:]
    rgb_driver.to_hex_color(color)
    redirect("/")

@route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root='static')

run(host='0.0.0.0', port=8080)
