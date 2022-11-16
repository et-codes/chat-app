import { ListGroup } from "react-bootstrap";

const Users = ({ users, activeUser }) => {
  const userList = [];
  if (users.length > 0) {
    users.forEach(user => {
      let variant = '';
      if (user === activeUser) variant = 'success';
      userList.push(
        <ListGroup.Item key={user} variant={variant}>
          {user}
        </ListGroup.Item>
      );
    });
  }

  return (
    <div>
      <div className="h5 mb-2 text-secondary">Users Online</div>
      <ListGroup variant="flush">
        {userList}
      </ListGroup>
    </div>
  );
}

export default Users;