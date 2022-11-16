# Yadda Yadda Yadda: Real-time Chat App

_Note: Backend code can be found [here](https://github.com/et-codes/chat-backend)._

### Try Yadda<sup>3</sup> [here](https://et-chat-app.herokuapp.com/)!

![screenshot](public/screenshot.png)

## Using the app:

- Log into the app to be able to post messages. Check the "Register new account" box to create a new account.
- If you wish only to view the messages, close the login pop-up and browse as Guest.
- Click on the channel name to the left to change channels.

## Installation instructions

Follow the steps below to run your own local copy of [Yadda<sup>3</sup>](https://et-chat-app.herokuapp.com/).

1. Clone both the [chat-frontend](https://github.com/et-codes/chat-frontend) and [chat-backend](https://github.com/et-codes/chat-backend) repositories into a local project directory.
1. Let's start by setting up the back end first:
   1. Install the `poetry` dependency management tool. ([Link](https://python-poetry.org/docs/#installation))
   1. Run `poetry shell` in the `chat-backend` directory.
   1. Run `poetry install` in the `chat-backend` directory.
   1. Set environment variable `DEVELOPMENT_MODE` to `false`.
   1. Set environment variable `SECRET_KEY` to any string you want.
   1. Install [PostgreSQL](https://www.postgresql.org/download/) and create a new database.
   1. Set environment variable `DATABASE_CONNECTION` to the `postgresql://` protocol connection string for your database.
   1. Modify the `channel_list.txt` file with your list of desired channels. Note that the "Testing" channel is required if you want to run the `test.py` unit tests.
   1. Run `poetry run python db.py` to set up the database tables and populate the channel list. (You may need to use `poetry run python3 db.py` depending on your operating system.)
   1. If you wish to use the `test.py` unit tests, you will also need to create a test user account (you can do this from the chat app). Set environment variables `TEST_USERNAME` and `TEST_PASSWORD` to make the credentials available to the script.
1. Now for the front end:
   1. Run `npm install` in the `chat-frontend` directory.
   1. Set environment variable `REACT_APP_BACKEND` to `http://localhost:5000`.
   1. Set environment variable `REACT_APP_CORS_ORIGIN` to `http://localhost:3000`.
   1. Run `npm run build` command from the `chat-frontend` folder.
   1. Delete the existing `build` folder from the `chat-backend` directory.
   1. Move the new `build` folder from the `chat-frontend` directory to the `chat-backend` directory.
1. Run `poetry run python app.py` from the `chat-backend` directory. (You may need to use `poetry run python3 app.py` depending on your operating system.)
1. Navigate to `http://localhost:5000` and enjoy!

## Technical information

[Yadda<sup>3</sup>](https://et-chat-app.herokuapp.com/) uses HTTP and websockets communication between the client and the server.

- HTTP requests are used for client-initiated actions, such as loading the initial data set, logging in, and sending new messages.
- Websockets are used to push new data, such as messages from other users and the active user list, from the server to the clients.
- User data, messages, and the channels list are stored in a database. The back end makes database queries, formats the results, and sends them to the clients.

**Front End Details**

- Written with **HTML**, **CSS**, and **JavaScript**, using the **React** framework.
- Styling was achieved using [React Bootstrap](https://react-bootstrap.github.io/).
- Websockets communication is handled with the `socket.io-client` library.
- HTTP calls to the back end's API are supported with the `axios` library.
- Webtoken is stored in `localStorage` for persistent login between sessions.

**Back End Details**

- Written in **Python** with the **Flask** framework.
- Data is stored in a **PostgreSQL** database, using the `psycopg2` adapter.
- Websockets communication is handled using the `flask_socketio` module.
- Passwords are encrypted and validated using `bcrypt`.
- The app is hosted on [Heroku](https://www.heroku.com/home) and the database is hosted on [CockroachDB](https://www.cockroachlabs.com/).

## Author

Eric Thornton | [LinkedIn](https://www.linkedin.com/in/ethornton/) | [Twitter](https://twitter.com/eric__thornton)
