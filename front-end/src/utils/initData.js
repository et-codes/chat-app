import axios from 'axios';


const getHttpData = async (url) => {
  try {
    const response = await axios.get(url);
    return response.data;
  } catch (err) {
    console.error(err);
  }
}

const loadInitialData = async () => {
  // Get list of logged in users
  let url = `/api/users`;
  const users = await getHttpData(url);

  // Get list of channels
  url = `/api/channels`;
  const channels = await getHttpData(url);

  // Create unread messages flags for each channel
  // eslint-disable-next-line no-sequences
  const unread = channels.reduce((acc, c) => (acc[c] = 0, acc), {});

  // Get messages from database
  url = `/api/messages`;
  const messages = await getHttpData(url);

  // Check if user was previously logged in, and if token is expired
  let username = localStorage.getItem('username');
  let token = localStorage.getItem('token');
  if (token && username) {
    url = `/api/token`
    const expired = await axios.post(url, { token: token });
    if (expired.data.expired) {
      username = null;
      token = null;
      localStorage.removeItem('username');
      localStorage.removeItem('token');
    }
  }

  return {
    users: users,
    username: username,
    token: token,
    channels: channels,
    unread: unread,
    messages: messages
  }
}

export default loadInitialData;