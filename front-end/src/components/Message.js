const Message = ({ message, color }) => {
  return (
    <p key={message.message_id}>
      <span className={'fw-bold ' + color}>
        {message.user}
      </span>{' '}
      <span className={'text-muted small'}>
        [{
          new Date(message.created_on).toLocaleTimeString([],
            { timeStyle: 'short' })
        }]:
      </span>{' '}
      {message.text}
    </p>
  );
}

export default Message;