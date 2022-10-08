from flask import Flask, request
from flask_cors import CORS


app = Flask(__name__, static_folder='./build', static_url_path='/')
cors = CORS(app)


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.get('/api/users')
def return_all_users():
    return 'All users'


@app.get('/api/users/<user>')
def return_user(user):
    return f'User {user}'


@app.post('/api/users')
def add_user():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        json = request.json
        return f"Add user {json['user']}"
    else:
        return 'Content-Type not supported.'


@app.get('/api/messages')
def return_all_messages():
    return 'All messages'


@app.post('/api/messages')
def add_message():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        json = request.json
        return f"Add message {json['message']}"
    else:
        return 'Content-Type not supported.'


if __name__ == '__main__':
    app.run(debug=True)
