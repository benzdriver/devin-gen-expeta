/**
 * Unit tests for UI System Access Layer
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from '../../access/ui/src/ui_system';
import { act } from 'react-dom/test-utils';

global.fetch = jest.fn();

function mockFetchResponse(data) {
  global.fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => data,
  });
}

describe('UI System', () => {
  beforeEach(() => {
    global.fetch.mockClear();
  });

  test('renders main app components', () => {
    render(<App />);
    
    expect(screen.getByText('Expeta 2.0')).toBeInTheDocument();
    
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Process')).toBeInTheDocument();
    expect(screen.getByText('Clarify')).toBeInTheDocument();
    expect(screen.getByText('Generate')).toBeInTheDocument();
    expect(screen.getByText('Validate')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
    
    expect(screen.getByText(/© 2025 Expeta 2.0/)).toBeInTheDocument();
  });

  test('dashboard loads and displays stats', async () => {
    render(<App />);
    
    expect(screen.getByText('Loading dashboard...')).toBeInTheDocument();
    
    await waitFor(() => {
      expect(screen.getByText('Requirements')).toBeInTheDocument();
      expect(screen.getByText('Expectations')).toBeInTheDocument();
      expect(screen.getByText('Generations')).toBeInTheDocument();
      expect(screen.getByText('Validations')).toBeInTheDocument();
    });
  });

  test('process tab handles requirement submission', async () => {
    const mockResponse = {
      requirement: 'Create a user authentication system',
      clarification: {
        top_level_expectation: {
          name: 'User Authentication',
          description: 'A system for user authentication'
        }
      },
      success: true
    };
    mockFetchResponse(mockResponse);
    
    render(<App />);
    
    fireEvent.click(screen.getByText('Process'));
    
    const textarea = screen.getByPlaceholderText('Describe what you want to build...');
    fireEvent.change(textarea, { target: { value: 'Create a user authentication system' } });
    
    const submitButton = screen.getByText('Process Requirement');
    fireEvent.click(submitButton);
    
    expect(screen.getByText('Processing')).toBeInTheDocument();
    
    await waitFor(() => {
      expect(screen.getByText('Success')).toBeInTheDocument();
    });
  });

  test('clarify tab handles requirement clarification', async () => {
    const mockResponse = {
      top_level_expectation: {
        id: 'exp-12345678',
        name: 'User Authentication',
        description: 'A system for user authentication'
      }
    };
    mockFetchResponse(mockResponse);
    
    render(<App />);
    
    fireEvent.click(screen.getByText('Clarify'));
    
    const textarea = screen.getByPlaceholderText('Describe what you want to build...');
    fireEvent.change(textarea, { target: { value: 'Create a user authentication system' } });
    
    const submitButton = screen.getByText('Clarify Requirement');
    fireEvent.click(submitButton);
    
    expect(screen.getByText('Clarifying')).toBeInTheDocument();
    
    await waitFor(() => {
      expect(screen.getByText('Success')).toBeInTheDocument();
    });
  });

  test('generate tab handles code generation', async () => {
    const mockResponse = {
      generated_code: {
        language: 'python',
        files: [
          {
            path: 'auth/user.py',
            content: 'class User:\n    pass'
          }
        ]
      }
    };
    mockFetchResponse(mockResponse);
    
    render(<App />);
    
    fireEvent.click(screen.getByText('Generate'));
    
    const input = screen.getByPlaceholderText('e.g., exp-12345678');
    fireEvent.change(input, { target: { value: 'exp-12345678' } });
    
    const submitButton = screen.getByText('Generate Code');
    fireEvent.click(submitButton);
    
    expect(screen.getByText('Generating')).toBeInTheDocument();
    
    await waitFor(() => {
      expect(screen.getByText('Success')).toBeInTheDocument();
    });
  });

  test('handles API errors gracefully', async () => {
    global.fetch.mockRejectedValueOnce(new Error('API Error'));
    
    render(<App />);
    
    fireEvent.click(screen.getByText('Process'));
    
    const textarea = screen.getByPlaceholderText('Describe what you want to build...');
    fireEvent.change(textarea, { target: { value: 'Create a user authentication system' } });
    
    const submitButton = screen.getByText('Process Requirement');
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Error')).toBeInTheDocument();
    });
  });

  test('validates input before submission', async () => {
    render(<App />);
    
    fireEvent.click(screen.getByText('Process'));
    
    const submitButton = screen.getByText('Process Requirement');
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Error')).toBeInTheDocument();
      expect(screen.getByText('Please enter a requirement')).toBeInTheDocument();
    });
  });
});
