import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import axios from 'axios';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import Login from './Login';

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Mock Axios for a successful login response
jest.mock('axios');

describe('Login Component', () => {
  let originalConsoleError; // Store the original console.error method

  beforeEach(() => {
    // Mock console.error to prevent it from displaying error messages
    originalConsoleError = console.error;
    console.error = jest.fn();
  });

  afterEach(() => {
    // Restore the original console.error method after each test
    console.error = originalConsoleError;
  });

  it('should render login form', () => {
    const { container } = render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    );

    expect(container.querySelector('h2').textContent).toBe('Login');
    expect(container.querySelector('label[for="username"]')).toBeInTheDocument();
    expect(container.querySelector('label[for="password"]')).toBeInTheDocument();
    expect(container.querySelector('button').textContent).toBe('Login');
  });

  it('should handle login success', async () => {
    // Mock Axios for a successful login response
    axios.post.mockResolvedValueOnce({ status: 200, data: { token: 'your-valid-token' } });

    // Mock the onLogin function
    const onLogin = jest.fn();
    
    const { container } = render(
      <MemoryRouter initialEntries={['/']}>
        <Routes>
          <Route path="/" element={<></>} />
          <Route path="/books" element={<div data-testid="books-page">Books Page</div>} />
        </Routes>
        <Login onLogin={onLogin} />
      </MemoryRouter>
    );

    fireEvent.change(container.querySelector('.username-input'), { target: { value: 'your-username' } });
    fireEvent.change(container.querySelector('.password-input'), { target: { value: 'your-password' } });
    fireEvent.click(container.querySelector('.login-button')); // Use className instead of id

    await waitFor(() => {
      // Verify that onLogin is called with the expected arguments
      expect(onLogin).toHaveBeenCalledWith('your-username', 'your-valid-token');
      expect(container.querySelector('.error')).not.toBeInTheDocument(); // Use className instead of id
    });
  });

  it('should handle login failure', async () => {
    // Mock Axios for a failed login response
    axios.post.mockRejectedValueOnce(new Error('Login failed'));

    const { container } = render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    );
    
    fireEvent.click(container.querySelector('.login-button')); // Use className instead of id

    await waitFor(() => {
      expect(container.querySelector('.error')).toBeInTheDocument(); // Use className instead of id
    });
  });
});
