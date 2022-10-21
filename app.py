import tokens
import bcrypt
import db
import json
import os
from dotenv import load_dotenv
from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO


# Load environment variables
load_dotenv()
SECRET_KEY = os.environ.get('SECRET_KEY')

# Set up Flask
app = Flask(__name__, static_folder='./build', static_url_path='/')
app.config['SECRET_KEY'] = SECRET_KEY
CORS(app, resources={r'/*': {'origins': '*'}})

# Set up websockets
socketio = SocketIO(app, cors_allowed_origins='*')

active_users = []
active_sessions = {}
socketio.emit('ping', broadcast=True)

# HTTP routes
@app.get('/api/users')
def return_active_users():
    return active_users


@app.get('/api/users/<username>')
def return_user(username):
    user = db.get_user(username)
    if user is not None:
        return user
    else:
        return 'User not found.'


@app.post('/api/users')
def add_user():
    (username, password) = request.json.values()
    
    salt = bcrypt.gensalt()
    password = password.encode('utf-8')

    hashed = bcrypt.hashpw(password, salt).decode('utf-8')

    created_user = db.create_user({
        'username': username,
        'password': hashed
    })
    
    return created_user


@app.post('/api/login')
def login_user():
    (username, password) = request.json.values()

    password = password.encode('utf-8')
    saved_password = db.get_user(username)['password'].encode('utf-8')
    
    if bcrypt.checkpw(password, saved_password):
        token = tokens.create_token(username)
        return token
    else:
        return 'Incorrect password.'

@app.post('/api/logout')
def logout_user():
    username = request.json['username']
    if username in active_users:
        active_users.remove(username)

    sessions = active_sessions.copy()
    for sid, user in sessions.items():
        if user == username:
            del active_sessions[sid]

    socketio.emit('active_users', active_users, broadcast = True)
    return username


@app.get('/api/channels')
def return_all_channels():
    return db.get_channels()


@app.get('/api/messages')
def return_all_messages():
    return db.get_messages()


@app.post('/api/messages')
def create_message():
    message = request.json
    new_msg = db.create_message(message)
    if new_msg is not None:
        socketio.send(json.dumps(new_msg), broadcast=True)
        return 'Message created.'
    else:
        return 'Server error.'


@app.route('/', defaults={'path': ''})
@app.route('/<string:path>')
def index(path):
    return app.send_static_file('index.html')


# WEBSOCKET handling
@socketio.on('connect')
def connect():
    if request.sid not in active_sessions:
        active_sessions[request.sid] = None


@socketio.on('login')
def handle_login(username):
    if username not in active_users:
        active_users.append(username)
        active_sessions[request.sid] = username
        db.login_user(username)

    socketio.emit('active_users', active_users, broadcast = True)


@socketio.on('disconnect')
def disconnect():
    if request.sid in active_sessions:
        disconnected_user = active_sessions[request.sid]
        del active_sessions[request.sid]

    if disconnected_user in active_users:
        active_users.remove(disconnected_user)

    socketio.emit('active_users', active_users, broadcast = True)


@socketio.on('ping')
def ping(username):
    # Rebuild user list after restarting server
    if username not in active_users:
        active_users.append(username)
        active_sessions[request.sid] = username
        socketio.emit('active_users', active_users, broadcast = True)


if __name__ == '__main__':
    socketio.run(app, debug=True)
