import { Button, Form } from 'react-bootstrap';
import { useState } from 'react';

const MessageForm = ({ handleSubmit, enabled }) => {
  const [message, setMessage] = useState([]);

  const handleChange = (event) => setMessage(event.target.value);

  const submitMessage = (event) => {
    event.preventDefault();
    handleSubmit(message);
    setMessage('');
  }

  return (
    <Form onSubmit={submitMessage} className="mb-3 d-flex gap-2 align-items-end">
      <Form.Control
        type="text"
        placeholder="Enter your message here..."
        value={message}
        onChange={handleChange}
        disabled={!enabled}
      />
      <Button variant="primary" type="submit" disabled={!enabled}>
        Send
      </Button>
    </Form>
  );
}

export default MessageForm;