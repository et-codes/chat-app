
INSERT INTO messages(message_id, user_id, channel_id, text)
VALUES(DEFAULT, 2, 1, 'hi there')
RETURNING message_id, created_on;
