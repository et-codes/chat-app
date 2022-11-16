import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { io } from 'socket.io-client';
import './style.css';

const baseURL = process.env.REACT_APP_BACKEND;
const corsURL = process.env.REACT_APP_CORS_ORIGIN;
const isDevelopmentMode = process.env.DEVELOPMENT_MODE;
const socket = isDevelopmentMode === false
  ? io('/', {
    transports: ['websocket'],
    cors: { origin: corsURL }
  })
  : io(baseURL, {
    transports: ['websocket'],
    cors: { origin: corsURL }
  })

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App socket={socket} />
  </React.StrictMode>
);
