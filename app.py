import db
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
    users = db.get_users()
    for user in users:
        if user['username'] == username:
            print(f'Login request: {user["username"]}')
            return user
    return 'User not found.'


@app.post('/api/users')
def add_user():
    users = db.get_users()
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
    return db.get_channels()


@app.get('/api/messages')
def return_all_messages():
    return db.get_messages()


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
    saved_message = db.create_message(message)
    socketio.send(
        json.dumps(saved_message), 
        broadcast=True
    )
    print(f'New message by {saved_message["user"]} in {saved_message["channel"]}')


@socketio.on('login')
def handle_login(username):
    if username not in active_users:
        active_users.append(username)
        active_sessions[request.sid] = username
        timestamp = db.login_user(username)
        print(f'Logged in: {username} at {timestamp}')

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


if __name__ == '__main__':
    socketio.run(app, debug=True)
