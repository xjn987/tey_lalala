from flask import Flask, render_template, request, redirect, url_for, flash
from flask_socketio import SocketIO, join_room, leave_room, send

app = Flask(__name__)
app.secret_key = "secret_key"
socketio = SocketIO(app)

users = {}
rooms = set()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        room = request.form['room']

        if username not in users:
            users[username] = room
            rooms.add(room)
            return redirect(url_for('chat', username=username, room=room))
        else:
            flash('Username already taken!')
    return render_template('index.html')

@app.route('/chat/<username>/<room>')
def chat(username, room):
    if username in users and users[username] == room:
        return render_template('chat.html', username=username, room=room)
    else:
        return redirect(url_for('index'))

@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    send(f"{data['username']} has joined {room}.", room=room)

@socketio.on('leave')
def on_leave(data):
    room = data['room']
    leave_room(room)
    send(f"{data['username']} has left {room}.", room=room)

@socketio.on('message')
def handle_message(data):
    send(data, room=data['room'])

if __name__ == '__main__':
    socketio.run(app, debug=True)
