import axios from 'axios';
import { useState } from 'react';
import { Button, Form, Modal, Alert } from 'react-bootstrap';

const Login = ({
  show, setActiveUser, onHide, socket, setToken, setMainAlert, updateUnread
}) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [rePassword, setRePassword] = useState('');
  const [newAccount, setNewAccount] = useState(false);
  const [alert, setAlert] = useState({});

  const handleUsername = (event) => setUsername(event.target.value);
  const handlePassword = (event) => setPassword(event.target.value);
  const handleRePassword = (event) => setRePassword(event.target.value);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (newAccount) {
      if (await createAccount()) clearForm();
    } else {
      if (await loginUser()) clearForm();
    }
  }

  const createAccount = async () => {
    if (password !== rePassword) {
      setAlert({ text: 'Passwords do not match.', variant: 'danger' });
      setPassword('');
      setRePassword('');
      return false;
    }

    try {
      const userCheck = await axios.get(`/api/users/${username}`);
      setAlert({
        text: `Username ${userCheck.username} already exists.`,
        variant: 'danger'
      });
      return false;
    } catch (error) {
      if (error.response.status === 404) {
        // User not found in DB, create new one
        const newUser = await axios.post(`/api/users`, {
          username: username,
          password: password
        });
        setAlert({
          text: `New user '${newUser.data.username}' created!`,
          variant: 'success'
        });
        setTimeout(() => {
          loginUser();
        }, 1500);
      } else {
        setAlert({
          text: error.response.data,
          variant: 'danger'
        });
        return false;
      }
    }
  }

  const loginUser = async () => {
    try {
      await axios.get(`/api/users/${username}`);
    } catch (error) {
      setAlert({ text: 'Invalid username.', variant: 'danger' });
      return false;
    }

    try {
      const loginResponse = await axios.post(`/api/login`, {
        username: username,
        password: password
      });

      setToken(loginResponse.data.token);
      if (loginResponse.data.last_logout) {
        updateUnread(loginResponse.data.last_logout);
      }
      localStorage.setItem('token', loginResponse.data.token);
      localStorage.setItem('username', username);

      setMainAlert({
        message: `${username} logged in!`,
        variant: 'success'
      });
      setTimeout(() => setMainAlert({}), 3000);

      setActiveUser(username);
      socket.emit('login', username);
      clearForm();
      return true;

    } catch (error) {
      setAlert({ text: error.response.data, variant: 'danger' });
      return false;
    }
  }

  const clearForm = () => {
    setUsername('');
    setPassword('');
    setRePassword('');
    setNewAccount(false);
  }

  return (
    <Modal
      show={show}
      onHide={onHide}
      onExited={() => setAlert({})}
      backdrop='static'
      keyboard='false'
      centered
    >
      <Modal.Header closeButton>
        <Modal.Title>
          Login / Register
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Alert variant={alert.variant || 'primary'}>
          {alert.text || 'Please log in to send messages, or close this window and continue as a Guest with read-only access.'}
        </Alert>
        <Form.Check
          className="mb-3"
          type="checkbox"
          label="Register new account"
          onChange={() => setNewAccount(!newAccount)}
        />
        <Form onSubmit={handleSubmit} className="mb-3">
          <Form.Control className="mb-2"
            type="text"
            placeholder="Username"
            value={username}
            onChange={handleUsername}
          />
          <Form.Control className="mb-2"
            type="password"
            placeholder="Password"
            value={password}
            onChange={handlePassword}
          />
          {newAccount && <Form.Control className="mb-2 "
            type="password"
            placeholder="Re-enter password"
            value={rePassword}
            onChange={handleRePassword}
          />}
          <Button variant="primary" type="submit">
            {newAccount ? 'Register' : 'Login'}
          </Button>
        </Form>
      </Modal.Body>
    </Modal>
  );
}

export default Login;