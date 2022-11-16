import { Channels, Users } from './';

const Sidebar = (
  { channels, unread, activeChannel, users, activeUser, setActiveChannel }
) => {
  return (
    <div>
      <Channels
        channels={channels}
        unread={unread}
        activeChannel={activeChannel}
        setActiveChannel={setActiveChannel}
      />
      <Users
        users={users}
        activeUser={activeUser}
      />
    </div>
  );
}

export default Sidebar;