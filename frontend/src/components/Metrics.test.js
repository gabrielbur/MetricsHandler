import React from 'react';
import { render, fireEvent, waitFor, screen, act, within } from '@testing-library/react';
import '@testing-library/jest-dom';
import Metrics from './Metrics';

// Mock socket.io-client
const mockEmit = jest.fn();
const mockOn = jest.fn((event, cb) => {
  if (event === 'connect') {
    cb();
  }
});
const mockDisconnect = jest.fn();
jest.mock('socket.io-client', () => {
  return jest.fn(() => ({
    emit: mockEmit,
    on: mockOn,
    disconnect: mockDisconnect,
  }));
});

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor(callback) {
    this.callback = callback;
  }
  disconnect() {}
  observe(element, initObject = {}) {
    this.callback([{
      target: element,
      contentRect: {
        width: element.offsetWidth || 0,
        height: element.offsetHeight || 0,
        top: 0,
        left: 0,
        bottom: element.offsetHeight || 0,
        right: element.offsetWidth || 0
      }
    }]);
  }
  unobserve() {}
};

// Mock fetch
global.fetch = jest.fn().mockImplementation((url) => {
  if (url.includes('get_metric_names')) {
    return Promise.resolve({
      ok: true,
      json: () => Promise.resolve(['metric_example', 'another_metric']),
    });
  }
  if (url.includes('log_metrics')) {
    return Promise.resolve({
      ok: true,
      json: () => Promise.resolve({ message: 'Metric logged successfully' }),
    });
  }
  return Promise.reject(new Error('not found'));
});

window.alert = jest.fn();

describe('Metrics Component', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders Metrics component and handles socket connection', async () => {
    let container;
    await act(async () => {
      ({ container } = render(<Metrics />));
    });


    // Check for initial connection
    expect(mockOn).toHaveBeenCalledWith('connect', expect.any(Function));
    
    // Check for Metric Name label and select element
    const filterMetricPanel = container.querySelector('.graph-filters-panel');
    expect(within(filterMetricPanel).getByLabelText(/Metric Name:/i)).toBeInTheDocument();

    const logMetricPanel = container.querySelector ('.log-metric-panel');
    await act(async () => {
      fireEvent.change(within(logMetricPanel).getByLabelText(/Metric Name:/i), { target: { value: 'new_metric' } });
      fireEvent.change(within(logMetricPanel).getByLabelText(/Metric Value:/i), { target: { value: '123' } });
      fireEvent.click(container.querySelector ('.log-metric-button'));
    });

    // Assert fetch was called for logging metrics
    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:5000/metrics/log_metrics',
      expect.any(Object)
    );
    expect(window.alert).toHaveBeenCalledWith('Metric logged successfully');

  });
});
