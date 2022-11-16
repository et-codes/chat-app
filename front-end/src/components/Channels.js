import { Badge, ListGroup } from "react-bootstrap";

const Channels = ({ channels, unread, activeChannel, setActiveChannel }) => {
  const onChannelClick = (channel) => {
    setActiveChannel(channel);
  }

  const channelList = [];
  if (channels) {
    channels.forEach(channel => {
      let active = false;
      if (channel === activeChannel) active = true;
      channelList.push(
        <ListGroup.Item
          action
          key={channel}
          active={active}
          onClick={() => onChannelClick(channel)}
        >
          {channel}{' '}
          <Badge pill bg='success'>
            {unread[channel] > 0 ? unread[channel] : ''}
          </Badge>
        </ListGroup.Item>
      );
    });
  }

  return (
    <div>
      <div className="h5 mb-2 text-secondary">Channels</div>
      <ListGroup className="mb-4" variant="flush">
        {channelList}
      </ListGroup>
    </div>
  );
}

export default Channels;