import React, { useState, useEffect } from 'react';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { Line } from 'react-chartjs-2';
import io from 'socket.io-client';
import './Metrics.css';

import { Chart, CategoryScale, LinearScale, LineController, LineElement, PointElement } from 'chart.js';

Chart.register(CategoryScale, LinearScale, LineController, LineElement, PointElement);

const Metrics = () => {
    const [startDate, setStartDate] = useState(null);
    const [endDate, setEndDate] = useState(null);
    const [interval, setInterval] = useState('hour');
    const [metricsData, setMetricsData] = useState([]);
    const [error, setError] = useState('');
    const [metricNames, setMetricNames] = useState([]);
    const [selectedMetricName, setSelectedMetricName] = useState('metric_example');
    const [addZeros, setAddZeros] = useState(false);
    const [logMetricName, setLogMetricName] = useState('');
    const [logMetricValue, setLogMetricValue] = useState('');
    const [socketError, setSocketError] = useState('');
    const [logMetricError, setLogMetricError] = useState('');

    const cache_key = (name, startDate, endDate, interval, includeZeros) => {
        return `${name}_${startDate ? startDate.toISOString() : 'null'}_${endDate ? endDate.toISOString() : 'null'}_${interval}_${includeZeros}`;
    };

    useEffect(() => {
        const token = localStorage.getItem('token');
        const socket = io('http://localhost:5000', { query: { token } });

        socket.on('connect', () => {
            console.log('Connected to WebSocket');
            setSocketError('');
            requestMetrics(socket);
        });

        socket.on('metrics_data', (data) => {
            setMetricsData(data);
        });

        socket.on('metrics_update', (data) => {
            if (data.key === cache_key(selectedMetricName, startDate, endDate, interval, addZeros)) {
                setMetricsData(data.metrics);
            }
        });

        socket.on('metrics_update', (data) => {
            if (data.metrics) {
                if (data.key === cache_key(selectedMetricName, startDate, endDate, interval, addZeros)) {
                    setMetricsData(data.metrics);
                }
            } else if (data.name && data.value && data.timestamp) {
                const newMetricTimestamp = new Date(data.timestamp);
                const isWithinRange = (!startDate || newMetricTimestamp >= startDate) &&
                                      (!endDate || newMetricTimestamp <= endDate) &&
                                      data.name === selectedMetricName;

                if (isWithinRange) {
                    requestMetrics(socket);
                } else {
                    fetchMetricNames();
                }
            }
        });

        socket.on('connect_error', (err) => {
            console.error('Connection Error:', err);
            setSocketError('WebSocket connection error');
        });

        fetchMetricNames();

        return () => socket.disconnect();
    }, [selectedMetricName, startDate, endDate, interval, addZeros]);

    const requestMetrics = (socket) => {
        socket.emit('request_metrics', {
            name: selectedMetricName,
            startDate: startDate ? startDate.toISOString() : null,
            endDate: endDate ? endDate.toISOString() : null,
            interval: interval,
            include_zeros: addZeros
        });
    };

    const fetchMetricNames = async () => {
        try {
            const response = await fetch('http://localhost:5000/metrics/get_metric_names');
            if (!response.ok) {
                throw new Error('Failed to fetch metric names');
            }
            const data = await response.json();
            setMetricNames(data);

            if (!data.includes(selectedMetricName)) {
                if (data.length > 0) {
                    setSelectedMetricName(data[0]);
                } else {
                    setSelectedMetricName('');
                }
            }
        } catch (error) {
            console.error('Error:', error);
            setError('Failed to fetch metric names');
        }
    };

    const handleLogMetricSubmit = async (e) => {
        e.preventDefault();
        if (!logMetricName.trim()) {
            setLogMetricError('Please enter a metric name.');
            return;
        }
        const value = parseFloat(logMetricValue);
        if (isNaN(value)) {
            setLogMetricError('Please enter a valid number for the metric value.');
            return;
        }

        try {
            const token = localStorage.getItem('token');
            const response = await fetch('http://localhost:5000/metrics/log_metrics', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ name: logMetricName, value: value }),
            });

            if (!response.ok) {
                throw new Error('Failed to log metric');
            }

            setLogMetricName('');
            setLogMetricValue('');
            alert('Metric logged successfully');
        } catch (error) {
            setError(error.message);
        }
        if (!error) {
            setLogMetricError(''); // Clear log metric error on success
        }
    };

    const handleIntervalChange = (event) => {
        setInterval(event.target.value);
    };

    const chartData = {
        labels: metricsData.map(d => d._id),
        datasets: [
            {
                label: 'Average Value',
                data: metricsData.map(d => d.average_value),
                fill: false,
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            },
        ],
    };

    return (
        <div className="metrics-container">
            {socketError && <p className="error-message">{socketError}</p>}

            <div className="graph-filters-panel">
                <div className="metric-name-selector">
                    <label className="metric-label" htmlFor="metric-name-select">Metric Name:</label>
                    <select id="metric-name-select" value={selectedMetricName} onChange={e => setSelectedMetricName(e.target.value)}>
                        {metricNames.map(name => (
                            <option key={name} value={name}>{name}</option>
                        ))}
                    </select>
                </div>
                <br/>
                <div className="date-picker-container">
                    <div className="date-picker-group">
                        <label className="date-label" htmlFor="start-date-picker">Start Date:</label>
                        <DatePicker
                            id="start-date-picker"
                            selected={startDate}
                            onChange={date => setStartDate(date)}
                            showTimeSelect
                            dateFormat="Pp"
                        />
                    </div>
                    <div className="date-picker-group">
                        <label className="date-label" htmlFor="end-date-picker">End Date:</label>
                        <DatePicker
                            id="end-date-picker"
                            selected={endDate}
                            onChange={date => setEndDate(date)}
                            showTimeSelect
                            dateFormat="Pp"
                        />
                    </div>
                </div>
                <div className="interval-zeros-container">
                    <div className="interval-selector">
                        <label className="interval-label" htmlFor="interval-select">Interval:</label>
                        <select id="interval-select" value={interval} onChange={handleIntervalChange}>
                            <option value="day">Day</option>
                            <option value="hour">Hour</option>
                            <option value="minute">Minute</option>
                        </select>
                    </div>
                    <div className="add-zeros-checkbox">
                        <label htmlFor="add-zeros-checkbox">
                            <input
                                id="add-zeros-checkbox"
                                type="checkbox"
                                checked={addZeros}
                                onChange={() => setAddZeros(!addZeros)}
                            />
                            Add Zeros
                        </label>
                    </div>
                </div>
            </div>
            {error && <p className="error-message">{error}</p>}
            <div className="chart-container">
                <Line data={chartData} />
            </div>
            <br/>
            <br/>
            <br/>
            <div className="log-metric-panel">
                {logMetricError && <p className="error-message">{logMetricError}</p>}
                <h3>Log Metric</h3>
                <form onSubmit={handleLogMetricSubmit}>
                    <div>
                        <label htmlFor="metric-name-input">Metric Name:</label>
                        <input id="metric-name-input" type="text" value={logMetricName} onChange={e => setLogMetricName(e.target.value)} />
                    </div>
                    <div>
                        <label htmlFor="metric-value-input">Metric Value:</label>
                        <input id="metric-value-input" type="text" value={logMetricValue} onChange={e => setLogMetricValue(e.target.value)} />
                    </div>
                    <button type="submit" className='log-metric-button'>Log Metric</button>
                </form>
            </div>
        </div>
    );
};

export default Metrics;
