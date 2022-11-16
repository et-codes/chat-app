/* eslint-disable react-hooks/exhaustive-deps */
import axios from 'axios';
import { useState, useEffect, useRef } from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import loadInitialData from './utils/initData.js';
import 'bootstrap/dist/css/bootstrap.min.css';
import {
  Header, Sidebar, MessagePane, MessageForm, Login
} from './components';

const App = ({ socket }) => {
  const [activeUser, setActiveUser] = useState('');
  const [activeChannel, setActiveChannel] = useState('');
  const [showLogin, setShowLogin] = useState(false);
  const [users, setUsers] = useState([]);
  const [channels, setChannels] = useState([]);
  const [messages, setMessages] = useState([]);
  const [token, setToken] = useState('');
  const [alert, setAlert] = useState({});
  const [unread, setUnread] = useState({});

  const activeChannelRef = useRef();
  activeChannelRef.current = activeChannel;

  // Get initial data
  useEffect(() => {
    const fetchData = async () => {
      const initialData = await loadInitialData();
      if (initialData.username && initialData.token) {
        setActiveUser(initialData.username);
        setToken(initialData.token);
      }
      setUsers(initialData.users);
      setChannels(initialData.channels);
      setUnread(initialData.unread);
      setActiveChannel(initialData.channels[0]);
      setMessages(initialData.messages);
    }
    fetchData();
  }, []);

  // Set up websockets listeners
  useEffect(() => {
    if (socket) {
      socket.on('connect', (data) => {
        // Let the server know if we are logged in already
        if (activeUser) {
          socket.emit('ping', activeUser);
        }
      });

      socket.on('message', newMessage => {
        // Receive push for new messages
        updateMessages(JSON.parse(newMessage));
      });

      socket.on('active_users', active_users => {
        // Receive push when users log in or out
        updateActiveUsers(active_users);
      });

      return () => {
        socket.off('connect');
        socket.off('message');
        socket.off('active_users');
      };
    }
  }, []);

  const updateActiveUsers = (newUsers) => {
    setUsers(newUsers);
  }

  // Check if user is logged in
  useEffect(() => {
    if (activeUser) {
      // If user logged in during previous session, need to ping server to
      // update active user list
      socket.emit('ping', activeUser);
      setShowLogin(false);
    } else {
      setShowLogin(true);
    }
  }, [socket, activeUser]);

  // Scroll to bottom when new message is added
  useEffect(() => {
    const scrollDiv = document.querySelector('.MessagePane');
    scrollDiv.scrollTop = scrollDiv.scrollHeight;
  }, [messages]);

  // Scroll to bottom, clear unread when channel is changed
  useEffect(() => {
    const scrollDiv = document.querySelector('.MessagePane');
    scrollDiv.scrollTop = scrollDiv.scrollHeight;
    setUnread({ ...unread, [activeChannel]: 0 });
  }, [activeChannel]);

  // Update header when new token is set
  useEffect(() => {
    axios.defaults.headers.post['Authorization'] = `Bearer ${token}`;
  }, [token]);

  const updateMessages = (messageObject) => {
    setMessages(messages => [...messages, messageObject]);
    if (messageObject.channel !== activeChannelRef.current) {
      setUnread(unread => ({
        ...unread,
        [messageObject.channel]: unread[messageObject.channel] + 1
      }));
    }
  }

  const handleNewMessage = async (message) => {
    const newMessage = {
      user: activeUser,
      text: message,
      channel: activeChannel
    };
    const url = `/api/messages`;
    try {
      await axios.post(url, newMessage);
    } catch (error) {
      setAlert({
        message: error.response.data,
        variant: error.response.status === 401 ? 'warning' : 'danger'
      });
      setTimeout(() => setAlert({}), 5000);
    }
  }

  const logoutUser = async () => {
    const url = `/api/logout`;
    await axios.post(url, { username: activeUser });
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    setActiveUser('');
  }

  const updateUnread = (lastLogout) => {
    const newUnread = { ...unread };
    messages.forEach(message => {
      if (new Date(message.created_on) > new Date(lastLogout)) {
        newUnread[message.channel]++;
      }
    });
    setUnread(newUnread);
    if (newUnread[activeChannel] > 0) {
      setTimeout(() => {
        setUnread({ ...newUnread, [activeChannel]: 0 })
      }, 5000);
    }
  }

  return (
    <div className="d-flex justify-content-center">
      <Container className="m-3">
        <Row className="border rounded">
          <Header
            user={activeUser}
            login={() => setShowLogin(true)}
            logout={logoutUser}
            alert={alert}
          />
        </Row>
        <Row>
          <Col className="col-3 border rounded">
            <Sidebar
              channels={channels}
              unread={unread}
              activeChannel={activeChannel}
              setActiveChannel={setActiveChannel}
              users={users}
              activeUser={activeUser}
            />
          </Col>
          <Col className="border rounded">
            <MessagePane
              messages={messages}
              activeUser={activeUser}
              activeChannel={activeChannel}
            />
            <MessageForm
              handleSubmit={handleNewMessage}
              enabled={Boolean(activeUser)}
            />
          </Col>
        </Row>
        <Login
          show={showLogin}
          setActiveUser={setActiveUser}
          onHide={() => setShowLogin(false)}
          socket={socket}
          setToken={setToken}
          setMainAlert={setAlert}
          updateUnread={updateUnread}
        />
      </Container>
    </div>
  );
}

export default App;
