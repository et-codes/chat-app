import { DateLine, Message } from "./";

const MessagePane = ({ messages, activeUser, activeChannel }) => {
  const messageList = [];
  if (messages.length > 0) {
    let date;
    messages.forEach(message => {
      let color = 'text-body';
      if (message.user === activeUser) color = 'text-success';

      const messageDate = new Date(message.created_on).toLocaleDateString();
      if (messageDate !== date && message.channel === activeChannel) {
        date = new Date(message.created_on).toLocaleDateString();
        messageList.push(
          <DateLine key={date} date={date} />
        );
      }

      if (message.channel === activeChannel) {
        messageList.push(
          <Message
            key={message.message_id}
            message={message}
            color={color}
          />
        );
      }
    });
  }

  return (
    <div className="MessagePane">
      {messageList}
    </div>
  );
}

export default MessagePane;