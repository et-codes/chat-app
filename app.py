import json
import os
import psycopg2
import psycopg2.extras
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO


# Load environment variables
load_dotenv()
DATABASE_HOST = os.environ.get('DATABASE_HOST')
DATABASE_NAME = os.environ.get('DATABASE_NAME')
DATABASE_USER = os.environ.get('DATABASE_USER')
DATABASE_PW = os.environ.get('DATABASE_PW')
SECRET_KEY = os.environ.get('SECRET_KEY')

# Set up Flask
app = Flask(__name__, static_folder='./build', static_url_path='/')
app.config['SECRET_KEY'] = SECRET_KEY
CORS(app, resources={r'/*': {'origins': '*'}})

# Set up websockets
socketio = SocketIO(app, cors_allowed_origins='*')

# Connect to database
db_connection_string = ' '.join([
    f'host={DATABASE_HOST}',
    f'dbname={DATABASE_NAME}',
    f'user={DATABASE_USER}',
    f'password={DATABASE_PW}'
])
conn = psycopg2.connect(db_connection_string)
conn.autocommit = True
cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

active_users = []
active_sessions = {}

# HTTP routes
@app.get('/api/users')
def return_active_users():
    return active_users


@app.get('/api/users/<username>')
def return_user(username):
    for user in users:
        if user['username'] == username:
            print(f'Login request: {user["username"]}')
            return user
    return 'User not found.'


@app.post('/api/users')
def add_user():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        json = request.json
        user_id = max([user['user_id'] for user in users]) + 1
        new_user = {
            'user_id': user_id,
            'username': json['username'],
            'password': json['password']
        }
        users.append(new_user)
        print(f'New user created: {new_user["username"]}')
        return new_user
    else:
        return 'Content-Type not supported.'


@app.get('/api/channels')
def return_all_channels():
    query_channels = '''SELECT channel FROM channels'''
    cursor.execute(query_channels)
    result = cursor.fetchall()
    channels = [row['channel'] for row in result]
    return channels


@app.get('/api/messages')
def return_all_messages():
    query_messages = '''
        SELECT 
            message_id,
            messages.created_on,
            users.username AS user,
            channels.channel,
            text
        FROM messages
        INNER JOIN channels
        ON messages.channel_id = channels.channel_id
        INNER JOIN users
        ON messages.user_id = users.user_id;
    '''
    cursor.execute(query_messages)
    result = []
    for row in cursor.fetchall():
        result.append(dict(row))
    return result


@app.route('/', defaults={'path': ''})
@app.route('/<string:path>')
def index(path):
    return app.send_static_file('index.html')


# WEBSOCKET handling
@socketio.on('connect')
def connect():
    print(f'Connected: {request.sid}')
    if request.sid not in active_sessions:
        active_sessions[request.sid] = None
    socketio.emit('connect', f'Connected {request.sid}')


@socketio.on('message')
def handle_message(message):
    message = json.loads(message)
    
    cursor.execute('SELECT user_id FROM users WHERE username=%s', 
        (message["user"],))
    user_id = cursor.fetchone()[0]

    cursor.execute('SELECT channel_id FROM channels WHERE channel=%s',
        (message["channel"],))
    channel_id = cursor.fetchone()[0]

    sql = '''
        INSERT INTO messages (message_id, user_id, channel_id, text)
        VALUES (DEFAULT, %s, %s, %s)
        RETURNING message_id, created_on;
    '''
    cursor.execute(sql, (user_id, channel_id, message['text']))
    message_id, created_on = cursor.fetchone()
    
    message_object = {
        'message_id': message_id,
        'created_on': created_on.isoformat(),
        'user': message['user'],
        'text': message['text'],
        'channel': message['channel']
    }
    socketio.send(
        json.dumps(message_object), 
        broadcast=True
    )
    print(f'New message by {message_object["user"]} in {message_object["channel"]}')
    messages.append(message_object)


@socketio.on('login')
def handle_login(username):
    if username not in active_users:
        active_users.append(username)
        active_sessions[request.sid] = username
        print(f'Logged in: {username}')

    socketio.emit('active_users', active_users, broadcast = True)


@socketio.on('logout')
def handle_logout(username):
    if username in active_users:
        active_users.remove(username)
    sessions = active_sessions.copy()
    for sid, user in sessions.items():
        if user == username:
            del active_sessions[sid]

    print(f'Logged out: {username}')

    socketio.emit('active_users', active_users, broadcast = True)


@socketio.on('disconnect')
def disconnect():
    if request.sid in active_sessions:
        disconnected_user = active_sessions[request.sid]
        del active_sessions[request.sid]

    if disconnected_user in active_users:
        active_users.remove(disconnected_user)

    print(f'Disconnected: {disconnected_user}')

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
    'channel': 'General',
    'text': 'Lorem ipsum dolor sit, amet consectetur adipisicing elit. Saepe cupiditate cum aut distinctio, rem voluptatibus beatae, unde odit ad suscipit magni dignissimos veniam ea dolorum.'
  },
  {
    'message_id': 2,
    'created_on': '2022-10-08 12:23:25.909003',
    'user': 'other_guy',
    'channel': 'General',
    'text': 'Lorem ipsum dolor sit, amet consectetur adipisicing elit. Saepe cupiditate cum aut distinctio, rem voluptatibus beatae, unde odit ad suscipit magni dignissimos veniam ea dolorum.'
  },
  {
    'message_id': 3,
    'created_on': '2022-10-09 12:23:25.909003',
    'user': 'eric',
    'channel': 'General',
    'text': 'Lorem ipsum dolor sit, amet consectetur adipisicing elit. Saepe cupiditate cum aut distinctio, rem voluptatibus beatae, unde odit ad suscipit magni dignissimos veniam ea dolorum.'
  },
  {
    'message_id': 4,
    'created_on': '2022-10-09 12:25:25.909003',
    'user': 'other_guy',
    'channel': 'General',
    'text': 'Lorem ipsum dolor sit, amet consectetur adipisicing elit. Saepe cupiditate cum aut distinctio, rem voluptatibus beatae, unde odit ad suscipit magni dignissimos veniam ea dolorum.'
  },
  {
    'message_id': 5,
    'created_on': '2022-10-10 14:23:25.909003',
    'user': 'eric',
    'channel': 'General',
    'text': 'Lorem ipsum dolor sit, amet consectetur adipisicing elit. Saepe cupiditate cum aut distinctio, rem voluptatibus beatae, unde odit ad suscipit magni dignissimos veniam ea dolorum.'
  },
  {
    'message_id': 6,
    'created_on': '2022-10-10 16:23:25.909003',
    'user': 'other_guy',
    'channel': 'General',
    'text': 'Lorem ipsum dolor sit, amet consectetur adipisicing elit. Saepe cupiditate cum aut distinctio, rem voluptatibus beatae, unde odit ad suscipit magni dignissimos veniam ea dolorum.'
  }
]
# END DUMMY DATA


if __name__ == '__main__':
    socketio.run(app, debug=True)
