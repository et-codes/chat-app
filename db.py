# Database access functions module
import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv


load_dotenv()
if os.environ.get('DEVELOPMENT_MODE') == 'true':
    db_connection_string = os.environ.get('DATABASE_CONNECTION_DEV')
else:
    db_connection_string = os.environ.get('DATABASE_CONNECTION')

print('Connecting to database...')
conn = psycopg2.connect(db_connection_string, connect_timeout=10)
print('Database connected.')
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
        updated_row = dict(row)
        updated_row['created_on'] = updated_row['created_on'].isoformat()
        result.append(updated_row)
    return result


def get_user(username):
    user_query = '''
        SELECT username, password
        FROM users WHERE username=%s
        '''
    cursor.execute(user_query, (username,));
    result = cursor.fetchone()
    if result is not None:
        return dict(result)
    else:
        return None


def get_channels():
    query_channels = 'SELECT channel FROM channels ORDER BY channel_id'
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
        RETURNING last_logout
    '''
    cursor.execute(sql, (username,))
    return cursor.fetchone()[0]


def logout_user(username):
    sql = '''
        UPDATE users
        SET last_logout = CURRENT_TIMESTAMP
        WHERE username = %s
        RETURNING last_logout
    '''
    cursor.execute(sql, (username,))
    return cursor.fetchone()[0]


def create_user(new_user):
    (username, password) = new_user.values()
    sql = '''
        INSERT INTO users (username, password)
        VALUES (%s, %s)
        RETURNING username;
    '''
    cursor.execute(sql, (username, password))
    return dict(cursor.fetchone())


def initialize_database():
    """
    Creates database tables and channel list. Use this function when setting up a new database.
    """
    channel_list = []
    with open('channel_list.txt') as file:
        for channel in file.readlines():
            channel_list.append(f"('{channel.strip()}')")
    channel_string = ','.join(channel_list)

    sql_list = [
        '''
            CREATE TABLE IF NOT EXISTS users(
                user_id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL,
                created_on TIMESTAMP WITH TIME ZONE 
                    DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP WITH TIME ZONE,
                last_logout TIMESTAMP WITH TIME ZONE
            );
        ''',
        '''
            CREATE TABLE IF NOT EXISTS channels(
                channel_id SERIAL PRIMARY KEY,
                channel VARCHAR(50) UNIQUE NOT NULL,
                created_on TIMESTAMP WITH TIME ZONE 
                    DEFAULT CURRENT_TIMESTAMP
            );
        ''',
        '''
            CREATE TABLE IF NOT EXISTS messages(
                message_id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(user_id) NOT NULL,
                channel_id INTEGER REFERENCES channels(channel_id) NOT NULL,
                text VARCHAR(512) NOT NULL,
                created_on TIMESTAMP WITH TIME ZONE 
                    DEFAULT CURRENT_TIMESTAMP
            );
        ''',
        f'''
            INSERT INTO channels(channel)
            VALUES
                {channel_string}
            ON CONFLICT(channel) DO NOTHING;
        '''
    ]

    for sql in sql_list:
        cursor.execute(sql)


if __name__ == '__main__':
    print('Running DB initialization...')
    initialize_database()
