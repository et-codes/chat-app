from datetime import datetime
from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO
import json


app = Flask(__name__, static_folder='./build', static_url_path='/')
app.config['SECRET_KEY'] = 'et-codes'
CORS(app, resources={r'/*': {'origins': '*'}})
socketio = SocketIO(app, cors_allowed_origins='*')

active_users = []
active_sessions = {}

# HTTP routes
@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.get('/api/users')
def return_active_users():
    return active_users


@app.get('/api/users/<user>')
def return_user(user):
    return f'User {user}'


@app.post('/api/users')
def add_user():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        json = request.json
        created_on = datetime.today().isoformat()
        return f"Added user {json['user']} on {created_on}"
    else:
        return 'Content-Type not supported.'


@app.get('/api/channels')
def return_all_channels():
    return channels


@app.get('/api/messages')
def return_all_messages():
    return messages


# WEBSOCKET handling
@socketio.on('connect')
def connect():
    print(f'{request.sid} has connected.')
    if request.sid not in active_sessions:
        active_sessions[request.sid] = None
    socketio.emit('connect', f'Connected {request.sid}')


@socketio.on('message')
def handle_message(message):
    message = json.loads(message)
    message_object = {
        'message_id': messages[-1]['message_id'] + 1,
        'created_on': datetime.today().isoformat(),
        'user': message['user'],
        'text': message['text']
    }
    socketio.send(
        json.dumps(message_object), 
        broadcast=True
    )
    print('New message created:', message_object)
    messages.append(message_object)


@socketio.on('login')
def handle_login(username):
    if username not in active_users:
        active_users.append(username)
        active_sessions[request.sid] = username
        print('Logged in:', username, request.sid)

    socketio.emit('active_users', active_users, broadcast = True)


@socketio.on('logout')
def handle_logout(username):
    active_users.remove(username)
    sessions = active_sessions.copy()
    for sid, user in sessions.items():
        if user == username:
            del active_sessions[sid]

    print('Logged out:', username, request.sid)

    socketio.emit('active_users', active_users, broadcast = True)


@socketio.on('disconnect')
def disconnect():
    if request.sid in active_sessions:
        disconnected_user = active_sessions[request.sid]
        del active_sessions[request.sid]

    active_users.remove(disconnected_user)

    print('Disconnected', disconnected_user, request.sid)

    socketio.emit('active_users', active_users, broadcast = True)


# BEGIN DUMMY DATA
users = [
    {'user_id': 1, 'username': 'eric', 'password': 'password'},
    {'user_id': 2, 'username': 'other_guy', 'password': 'password'},
    {'user_id': 3, 'username': 'Jimmy J', 'password': 'password'}
]

messages = [
  {
    'message_id': 1,
    'created_on': '2022-10-08 12:22:24.971424',
    'user': 'eric',
    'channel_id': 0,
    'text': 'Lorem ipsum dolor sit, amet consectetur adipisicing elit. Saepe cupiditate cum aut distinctio, rem voluptatibus beatae, unde odit ad suscipit magni dignissimos veniam ea dolorum.'
  },
  {
    'message_id': 2,
    'created_on': '2022-10-08 12:23:25.909003',
    'user': 'other_guy',
    'channel_id': 0,
    'text': 'Lorem ipsum dolor sit, amet consectetur adipisicing elit. Saepe cupiditate cum aut distinctio, rem voluptatibus beatae, unde odit ad suscipit magni dignissimos veniam ea dolorum.'
  },
  {
    'message_id': 3,
    'created_on': '2022-10-09 12:23:25.909003',
    'user': 'eric',
    'channel_id': 0,
    'text': 'Lorem ipsum dolor sit, amet consectetur adipisicing elit. Saepe cupiditate cum aut distinctio, rem voluptatibus beatae, unde odit ad suscipit magni dignissimos veniam ea dolorum.'
  },
  {
    'message_id': 4,
    'created_on': '2022-10-09 12:25:25.909003',
    'user': 'other_guy',
    'channel_id': 0,
    'text': 'Lorem ipsum dolor sit, amet consectetur adipisicing elit. Saepe cupiditate cum aut distinctio, rem voluptatibus beatae, unde odit ad suscipit magni dignissimos veniam ea dolorum.'
  },
  {
    'message_id': 5,
    'created_on': '2022-10-10 14:23:25.909003',
    'user': 'eric',
    'channel_id': 0,
    'text': 'Lorem ipsum dolor sit, amet consectetur adipisicing elit. Saepe cupiditate cum aut distinctio, rem voluptatibus beatae, unde odit ad suscipit magni dignissimos veniam ea dolorum.'
  },
  {
    'message_id': 6,
    'created_on': '2022-10-10 16:23:25.909003',
    'user': 'other_guy',
    'channel_id': 0,
    'text': 'Lorem ipsum dolor sit, amet consectetur adipisicing elit. Saepe cupiditate cum aut distinctio, rem voluptatibus beatae, unde odit ad suscipit magni dignissimos veniam ea dolorum.'
  }
]

channels = [
    'General', 'Random', 'Off-topic'
]

channel_list = [
    {'channel_id': 0, 'channel': 'General'},
    {'channel_id': 1, 'channel': 'Random'},
    {'channel_id': 2, 'channel': 'Off-topic'}
]

# END DUMMY DATA


if __name__ == '__main__':
    socketio.run(app, debug=True)
