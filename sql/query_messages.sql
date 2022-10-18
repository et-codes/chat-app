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