from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase

app = Flask(__name__)
app.config["SECRET_KEY"] = "hjhjsdahhds"
socketio = SocketIO(app)

rooms = {}

def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        
        if code not in rooms:
            break
    
    return code

@app.route("/", methods=["POST", "GET"])
def home():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if not name:
            return render_template("home.html", error="Please enter a name.", code=code, name=name)

        if join != False and not code:
            return render_template("home.html", error="Please enter a room code.", code=code, name=name)
        
        room = code
        if create != False:
            room = generate_unique_code(10)
            rooms[room] = {"members": 0, "messages": []}
        elif code not in rooms:
            return render_template("home.html", error="Room does not exist.", code=code, name=name)
        
        session["room"] = room
        session["name"] = name
        return redirect(url_for("room"))

    return render_template("home.html")

@app.route("/room")
def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))

    return render_template("room.html", code=room, messages=rooms[room]["messages"])

@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return 
    
    content = {
        "name": session.get("name"),
        "message": data["data"]
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get('name')} said: {data['data']}")

@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    send({"name": name, "message": "has entered the room"}, to=room)
    rooms[room]["members"] += 1
    print(f"{name} joined room {room}")

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]
    
    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} has left the room {room}")

if __name__ == "__main__":
    socketio.run(app, debug=True)
    
    

'''
@socketio.on('message')
def handle_message(data):
    print('received message: ' + data)
The above example uses string messages. Another type of unnamed events use JSON data:

@socketio.on('json')
def handle_json(json):
    print('received json: ' + str(json))
The most flexible type of event uses custom event names. The message data for these events can be string, bytes, int, or JSON:

@socketio.on('my event')
def handle_my_custom_event(json):
    print('received json: ' + str(json))
Custom named events can also support multiple arguments:

@socketio.on('my_event')
def handle_my_custom_event(arg1, arg2, arg3):
    print('received args: ' + arg1 + arg2 + arg3)
When the name of the event is a valid Python identifier that does not collide with other defined symbols, the @socketio.event decorator provides a more compact syntax that takes the event name from the decorated function:

@socketio.event
def my_custom_event(arg1, arg2, arg3):
    print('received args: ' + arg1 + arg2 + arg3)
Named events are the most flexible, as they eliminate the need to include additional metadata to describe the message type. The names message, json, connect and disconnect are reserved and cannot be used for named events.

Flask-SocketIO also supports SocketIO namespaces, which allow the client to multiplex several independent connections on the same physical socket:

@socketio.on('my event', namespace='/test')
def handle_my_custom_namespace_event(json):
    print('received json: ' + str(json))
When a namespace is not specified a default global namespace with the name '/' is used.

For cases when a decorator syntax isn’t convenient, the on_event method can be used:

def my_function_handler(data):
    pass

socketio.on_event('my event', my_function_handler, namespace='/test')
Clients may request an acknowledgement callback that confirms receipt of a message they sent. Any values returned from the handler function will be passed to the client as arguments in the callback function:

@socketio.on('my event')
def handle_my_custom_event(json):
    print('received json: ' + str(json))
    return 'one', 2
In the above example, the client callback function will be invoked with two arguments, 'one' and 2. If a handler function does not return any values, the client callback function will be invoked without arguments.

Sending Messages
SocketIO event handlers defined as shown in the previous section can send reply messages to the connected client using the send() and emit() functions.

The following examples bounce received events back to the client that sent them:

from flask_socketio import send, emit

@socketio.on('message')
def handle_message(message):
    send(message)

@socketio.on('json')
def handle_json(json):
    send(json, json=True)

@socketio.on('my event')


@socketio.on('message')
def handle_message(data):
    print('received message: ' + data)
The above example uses string messages. Another type of unnamed events use JSON data:

@socketio.on('json')
def handle_json(json):
    print('received json: ' + str(json))
The most flexible type of event uses custom event names. The message data for these events can be string, bytes, int, or JSON:

@socketio.on('my event')
def handle_my_custom_event(json):
    print('received json: ' + str(json))
Custom named events can also support multiple arguments:

@socketio.on('my_event')
def handle_my_custom_event(arg1, arg2, arg3):
    print('received args: ' + arg1 + arg2 + arg3)
When the name of the event is a valid Python identifier that does not collide with other defined symbols, the @socketio.event decorator provides a more compact syntax that takes the event name from the decorated function:

@socketio.event
def my_custom_event(arg1, arg2, arg3):
    print('received args: ' + arg1 + arg2 + arg3)
Named events are the most flexible, as they eliminate the need to include additional metadata to describe the message type. The names message, json, connect and disconnect are reserved and cannot be used for named events.

Flask-SocketIO also supports SocketIO namespaces, which allow the client to multiplex several independent connections on the same physical socket:

@socketio.on('my event', namespace='/test')
def handle_my_custom_namespace_event(json):
    print('received json: ' + str(json))
When a namespace is not specified a default global namespace with the name '/' is used.

For cases when a decorator syntax isn’t convenient, the on_event method can be used:

def my_function_handler(data):
    pass

socketio.on_event('my event', my_function_handler, namespace='/test')
Clients may request an acknowledgement callback that confirms receipt of a message they sent. Any values returned from the handler function will be passed to the client as arguments in the callback function:

@socketio.on('my event')
def handle_my_custom_event(json):
    print('received json: ' + str(json))
    return 'one', 2
In the above example, the client callback function will be invoked with two arguments, 'one' and 2. If a handler function does not return any values, the client callback function will be invoked without arguments.

Sending Messages
SocketIO event handlers defined as shown in the previous section can send reply messages to the connected client using the send() and emit() functions.

The following examples bounce received events back to the client that sent them:

from flask_socketio import send, emit

@socketio.on('message')
def handle_message(message):
    send(message)

@socketio.on('json')
def handle_json(json):
    send(json, json=True)

@socketio.on('my event')
'''