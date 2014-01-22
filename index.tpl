<!doctype html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, user-scalable=no">
    <title></title>

    <link rel="stylesheet" href="/static/farbtastic/farbtastic.css"></link>
    <style>
        input[type="range"] {
            width: 100%;
        }
    </style>
</head>
<body>
    <form>
        <label for="hsl">HSL</label><br>
        <input id="hue" name="hue" type="range" min="0" max="1" step=".003921569"><br>
        <input id="sat" name="sat" type="range" min="0" max="1" step=".003921569" value="1"><br>
        <input id="light" name="light" type="range" min="0" max="1" step=".003921569"><br>
        <hr>
        <label for="colorpicker">Color wheel</label>
        <div id="colorpicker"></div>
        <hr>
        <label for="brightness">Simple led brightness</label><br>
        <input id="brightness" name="brightness" type="range" min="0" max="4095" step="5">
    </form>
    <script src="/static/jquery-2.0.3.min.js"></script>
    <script src="/static/farbtastic/farbtastic.js"></script>

    <script type="text/javascript">
        $(document).ready(function() {
            if (!window.WebSocket) {
                if (window.MozWebSocket) {
                    window.WebSocket = window.MozWebSocket;
                } else {
                    console.log("No websockets. :()");
                }
            }
            var arr = document.URL.split('/');
            var result = arr[2];
            ws = new WebSocket('ws://' + result + '/control');
            ws.onopen = function(evt) {
                console.log('Websocket connection opened.');
            }
            ws.onmessage = function(evt) {
                console.log(evt.data);
            }
            ws.onclose = function(evt) {
                console.log('WebSocket connection closed.');
            }
            $('#colorpicker').farbtastic(function(c) {
                ws.send(JSON.stringify({action: "color", value: c}));
            });
            $('#brightness').change(function(e) {
                ws.send(JSON.stringify({action: "set_simple", value: e.target.valueAsNumber}));
            });
            $('#hue, #sat, #light').change(function() {
                var color = HSVtoRGB(parseFloat($('#hue').val()), parseFloat($('#sat').val()), parseFloat($('#light').val()));
                ws.send(JSON.stringify({action: "color", value: rgbToHex(color.r, color.g, color.b)}));
            });
        });
        function HSVtoRGB(h, s, v) {
            var r, g, b, i, f, p, q, t;
            if (h && s === undefined && v === undefined) {
                s = h.s, v = h.v, h = h.h;
            }
            i = Math.floor(h * 6);
            f = h * 6 - i;
            p = v * (1 - s);
            q = v * (1 - f * s);
            t = v * (1 - (1 - f) * s);
            switch (i % 6) {
                case 0: r = v, g = t, b = p; break;
                case 1: r = q, g = v, b = p; break;
                case 2: r = p, g = v, b = t; break;
                case 3: r = p, g = q, b = v; break;
                case 4: r = t, g = p, b = v; break;
                case 5: r = v, g = p, b = q; break;
            }
            return {
                r: Math.floor(r * 255),
                g: Math.floor(g * 255),
                b: Math.floor(b * 255)
            };
        }
        function componentToHex(c) {
            var hex = c.toString(16);
            return hex.length == 1 ? "0" + hex : hex;
        }
        function rgbToHex(r, g, b) {
            return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
        }
    </script>
</body>
</html>
