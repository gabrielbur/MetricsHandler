import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './Login.css';

const Login = ({ onLogin, setIsLoggedIn }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      validateToken(token);
    }
  }, []);

  const handleLogin = async () => {
    try {
      const response = await axios.post('http://localhost:5000/login', {
        username,
        password,
      });

      if (response.status === 200) {
        const token = response.data.token;
        console.log("login success");
        onLogin(username, token);
        logLoginMetric(1); // Log successful login
        navigate('/books', { replace: true }); 
      } else {
        console.log("login failed");
        setError('Login failed. Please check your credentials.');
        logLoginMetric(0); // Log failed login
      }
    } catch (error) {
      setError('Login failed. Please check your credentials.');
      console.error('Login failed:', error);
      logLoginMetric(0); // Log failed login
    }
  };

  const validateToken = async (token) => {
    try {
      const response = await axios.post('http://localhost:5000/validate_token', {
        token,
      });
      if (response.status === 200 && response.data.valid) {
        setIsLoggedIn(true); // Update the state in App.js
        navigate('/books', { replace: true }); // Use navigate with replace option
      }
    } catch (error) {
      console.error('Token validation failed:', error);
    }
  };

  const logLoginMetric = async (value) => {
    try {
      await axios.post('http://localhost:5000/metrics/log_metrics', {
        name: 'login',
        value,
      });
    } catch (error) {
      console.error('Error logging login metric:', error);
    }
  };
  
  return (
    <div className="container">
      <h2>Login</h2>
      <div>
        <label htmlFor="username">Username:</label>
        <input
          type="text"
          id="username"
          className="username-input"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
      </div>
      <div>
        <label htmlFor="password">Password:</label>
        <input
          type="password"
          id="password"
          className="password-input"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </div>
      {error && <p className="error" id="error-message">{error}</p>}
      <button onClick={handleLogin} className="login-button" id="login-button">Login</button>
    </div>
  );
};

export default Login;
