INSERT INTO messages(message_id, user_id, channel_id, text)
VALUES(DEFAULT, 2, 1, 'hey, whats up?')
RETURNING message_id;