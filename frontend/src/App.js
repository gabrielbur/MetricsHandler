// App.js
import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Books from './components/Books';
import Metrics from './components/Metrics'; 
import './App.css';

const App = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const handleLogin = (username, token) => {
    localStorage.setItem('token', token);
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsLoggedIn(false);
  };

  return (
    <Router>
      <header>
        <h1>Metrics App</h1>
        {isLoggedIn && (
          <nav>
            <ul>
              <li><Link to="/books">Books</Link></li>
              <li><Link to="/metrics">Metrics</Link></li>
              <li onClick={handleLogout}>Logout</li>
            </ul>
          </nav>
        )}
      </header>
      <Routes>
        <Route path="/" element={!isLoggedIn ? <Navigate to="/login" /> : <Navigate to="/books" />} />
        <Route path="/login" element={<Login onLogin={handleLogin} />} />
        <Route path="/books" element={isLoggedIn ? <Books /> : <Navigate to="/login" />} />
        <Route path="/metrics" element={isLoggedIn ? <Metrics /> : <Navigate to="/login" />} /> 
      </Routes>
    </Router>
  );
};

export default App;
