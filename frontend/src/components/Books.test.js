import React from 'react';
import { render, waitFor } from '@testing-library/react';
import axios from 'axios';
import { MemoryRouter } from 'react-router-dom';
import Books from './Books';

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Mock Axios for successful response
jest.mock('axios');

describe('Books Component', () => {
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

  it('should render books', async () => {

    const mockToken = 'your-mock-token';
    jest.spyOn(window.localStorage.__proto__, 'getItem').mockReturnValueOnce(mockToken);


    // Mock Axios to return a list of books
    const booksData = [
      { id: 1, title: 'Book 1', author: 'Author 1', isbn: 'ISBN 1' },
      { id: 2, title: 'Book 2', author: 'Author 2', isbn: 'ISBN 2' },
    ];
    axios.get.mockResolvedValueOnce({ data: { books: booksData } });

    const { getByText } = render(
      <MemoryRouter>
        <Books />
      </MemoryRouter>
    );

    await waitFor(() => expect(axios.get).toHaveBeenCalled());

    // Wait for Axios request to resolve
    await waitFor(() => {
      for (const book of booksData) {
        expect(getByText(book.title)).toBeInTheDocument();
        expect(getByText(book.author)).toBeInTheDocument();
        expect(getByText(book.isbn)).toBeInTheDocument();
      }
    });
  });

  it('should handle error when fetching books', async () => {
    
    const mockToken = 'your-mock-token';
    jest.spyOn(window.localStorage.__proto__, 'getItem').mockReturnValueOnce(mockToken);

    // Mock Axios to return an error response
    axios.get.mockRejectedValueOnce(new Error('Failed to fetch books'));
    
    await waitFor(() => expect(axios.get).toHaveBeenCalled());
    
    const { container, getByText } = render(
      <MemoryRouter>
        <Books />
      </MemoryRouter>
    );

    // Wait for Axios request to reject and display error message
    await waitFor(() => {
      expect(getByText('Failed to fetch books. Please try again later.')).toBeInTheDocument();
    });
  });

  it('should navigate to login if token is not present', async () => {
    // Mock localStorage to not contain a token
    jest.spyOn(window.localStorage.__proto__, 'getItem').mockReturnValueOnce(null);

    render(
      <MemoryRouter>
        <Books />
      </MemoryRouter>
    );

    // Check if useNavigate is called with '/login'
    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });
});
