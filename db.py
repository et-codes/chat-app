# Database access functions module
import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

# Import environment variables
load_dotenv()
DATABASE_HOST = os.environ.get('DATABASE_HOST')
DATABASE_NAME = os.environ.get('DATABASE_NAME')
DATABASE_USER = os.environ.get('DATABASE_USER')
DATABASE_PW = os.environ.get('DATABASE_PW')

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


def get_messages():
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
        ON messages.user_id = users.user_id
        ORDER BY messages.created_on;
    '''
    cursor.execute(query_messages)
    result = []
    for row in cursor.fetchall():
        result.append(dict(row))
    return result


def get_users():
    query_users = 'SELECT username, password FROM users'
    cursor.execute(query_users)
    result = []
    for row in cursor.fetchall():
        result.append(dict(row))
    return result


def get_channels():
    query_channels = 'SELECT channel FROM channels'
    cursor.execute(query_channels)
    result = cursor.fetchall()
    channels = [row['channel'] for row in result]
    return channels


def create_message(message):
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
    return message_object


def login_user(username):
    sql = '''
        UPDATE users
        SET last_login = CURRENT_TIMESTAMP
        WHERE username = %s
        RETURNING last_login
    '''
    cursor.execute(sql, (username,))
    return cursor.fetchone()[0]


def get_user(username):
    user_query = 'SELECT username, password FROM users WHERE username=%s'
    cursor.execute(user_query, (username,));
    result = cursor.fetchone()
    if result is not None:
        return dict(result)
    else:
        return None


def create_user(new_user):
    (username, password) = new_user.values()
    sql = '''
        INSERT INTO users (username, password)
        VALUES (%s, %s)
        RETURNING username;
    '''
    cursor.execute(sql, (username, password))
    return dict(cursor.fetchone())