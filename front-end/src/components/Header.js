import { Alert, Container, Row, Col, Dropdown } from 'react-bootstrap';

const Header = ({ user, login, logout, alert }) => {
  const loggedIn = Boolean(user);
  return (
    <Container>
      <Row className="py-1 my-1 d-flex align-items-center justify-content-between">
        <Col className="h2 m-0 col-3">
          <span>Yadda<sup className="text-primary">3</sup></span>
          <a
            href="https://github.com/et-codes/chat-frontend"
            className="link-secondary text-decoration-none"
            rel="noreferrer"
            target="_blank"
          >
            <span className="fs-6 m-3">[GitHub]</span>
          </a>
        </Col>
        <Col>
          <Alert
            className="text-center m-0 p-1"
            variant={alert.variant}
            show={Boolean(alert.message)}
          >
            {alert.message}
          </Alert>
        </Col>
        <Col className="col-3 d-flex flex-row-reverse align-items-center">
          <Dropdown>
            <Dropdown.Toggle variant="success">
              <span>{user || 'Guest'}</span>
            </Dropdown.Toggle>
            <Dropdown.Menu>
              <Dropdown.Item onClick={login} disabled={loggedIn}>
                Login
              </Dropdown.Item>
              <Dropdown.Item onClick={logout} disabled={!loggedIn}>
                Logout
              </Dropdown.Item>
            </Dropdown.Menu>
          </Dropdown>
        </Col>
      </Row>
    </Container>
  );
}

export default Header;