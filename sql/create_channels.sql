INSERT INTO channels(channel)
VALUES
	('General'), 
	('Coding'),
	('Drumming'),
	('Random'),
	('Testing')
ON CONFLICT(channel) DO NOTHING;