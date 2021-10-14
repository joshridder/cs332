# Josh Ridder for CS332 at Calvin University 10-13-21


from browser import document, html, DOMEvent, websocket
from javascript import JSON

WIDTH = 600
HEIGHT = 600

SERVER_PORT = 8001


my_lastx = None
my_lasty = None
ws = None
color_choice = 'black'      # default value

# Get the URL host:port, split on ':', and use the host part
# as the machine on which the websockets server is running.
server_ip = document.location.host.split(':')[0]


# " TODO: store last_x and last_y values *for each client* in some data structure
# defined here. "

# Instead of storing last_x and last_y for each client, I sent a pair of
# coordinates at a time. This will increase the amount of data sent by each
# client, but will make another data structure deticated to storing last_x
# and last_y values for each client redundant.


def handle_mousemove(ev: DOMEvent):
    '''On behalf of all that is good, I apologize for using global
    variables in this code. It is difficult to avoid them when you
    have callbacks like we do here, unless you start creating classes, etc.
    That seemed like overkill for this relatively simple application.'''

    global ctx
    global my_lastx, my_lasty
    global ws

    # This is the first event or the mouse is being moved without a button
    # being pushed -- don't draw anything, but record where the mouse is.
    if my_lastx is None or ev.buttons == 0:
        my_lastx = ev.x
        my_lasty = ev.y
        # "TODO: send data to server."
        # Sending 2 pairs of coordinates means we don't have to send the location
        # of the mouse unless the mouse button is being pressed.

    else:
        ctx.beginPath()
        ctx.moveTo(my_lastx, my_lasty)
        ctx.lineTo(ev.x, ev.y)
        ctx.strokeStyle = color_choice
        ctx.stroke()
        # send data to server.
        data = JSON.stringify({"x0": my_lastx, "y0": my_lasty, "x1": ev.x, "y1": ev.y, "color": color_choice})
        ws.send(data)
        

        # Store new (x, y) as the last point.
        my_lastx = ev.x
        my_lasty = ev.y


def handle_other_client_data(data):
    ''' Uses a set of x and y coordinate pairs received from another client to draw a line '''
    global ctx

    ctx.beginPath()
    ctx.moveTo(data["x0"], data["y0"])
    ctx.lineTo(data["x1"], data["y1"])
    ctx.strokeStyle = data["color"]
    ctx.stroke()


def on_mesg_recv(evt):
    '''message received from server'''
    data = JSON.parse(evt.data)
    handle_other_client_data(data)


def set_color(evt):
    global color_choice
    # Get the value of the input box:
    color_choice = document['color_input'].value
    print('color_choice is now', color_choice)


def set_server_ip(evt):
    global server_ip
    global ws
    server_ip = document['server_input'].value
    ws = websocket.WebSocket(f"ws://{server_ip}:{SERVER_PORT}/")
    ws.bind('message', on_mesg_recv)


# ----------------------- Main -----------------------------


canvas = html.CANVAS(width=WIDTH, height=HEIGHT, id="myCanvas")
document <= canvas
ctx = document.getElementById("myCanvas").getContext("2d")

canvas.bind('mousemove', handle_mousemove)

document <= html.P()
color_btn = html.BUTTON("Set color: ", Class="button")
color_btn.bind("click", set_color)
document <= color_btn
color_input = html.INPUT(type="text", id="color_input", value=color_choice)
document <= color_input

document <= html.P()
server_btn = html.BUTTON("Server IP address: ", Class="button")
server_btn.bind("click", set_server_ip)
document <= server_btn
server_txt_input = html.INPUT(type="text", id="server_input", value=server_ip)
document <= server_txt_input

ws = websocket.WebSocket(f"ws://{server_ip}:{SERVER_PORT}/")
ws.bind('message', on_mesg_recv)

# Phase 2
# If we wanted to allow a user to erase areas, we could simply set the
# brush color to the background color and increase the width, giving
# eraser-like functionality while not saving canvas state.
# We could add an "eraser" key to the dictionary, which would tell
# us if the user intends to erase content instead of draw lines, which
# would then set up the brush as previously specified.

# The protocol would need to include the text to be sent.
# If we wanted to be able to write text on the canvas, we would likely
# have to save the canvas' state in the server, or part of the canvas' state, in order
# to allow for a functioning backspace button that wouldn't simply erase
# everything beneath it. If we didn't save the state of the canvas, we might
# be able to "delete" text by simply using a block of the same color as the
# background of a set size to cover the text. Also, we have the option of simply
# not implementing a backspace function for text if we're so inclined.

# Taking and releasing control of the whiteboard would force our protocol
# to be stateful - the server would have to know who has taken control
# of the board in order to see if new lines on the board are draw by
# the user with current control. This user would also be the only one
# capable of releasing control of the board.