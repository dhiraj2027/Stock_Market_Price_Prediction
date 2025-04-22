import React, { useState } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2'; // Import Line chart from react-chartjs-2
import { Chart as ChartJS } from 'chart.js/auto'; // Auto register chart.js components

const Predictor = () => {
  const [company, setCompany] = useState('');
  const [date, setDate] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handlePredict = async (e) => {
    e.preventDefault();
    setError('');
    setResult(null);

    try {
      const res = await axios.post('http://127.0.0.1:5000/predict', {
        company,
        date,
      });
      setResult(res.data);
      console.log('Response data:', res);
    } catch (err) {
      if (err.response && err.response.data && err.response.data.error) {
        setError(err.response.data.error);
      } else {
        setError('Something went wrong!');
      }
    }
  };

  // Prepare data for the chart
  const chartData = result && {
    labels: Array.from({ length: 10 }, (_, idx) => `Day ${idx + 1}`),
    datasets: [
      {
        label: 'Predicted Price (₹)',
        data: result.predicted_close_prices_next_10_days,
        borderColor: 'rgba(75, 192, 192, 1)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        fill: true,
      },
      {
        label: 'Actual Price (₹)',
        data: result.actual_close_prices_next_10_days || Array(10).fill(null),
        borderColor: 'rgba(255, 99, 132, 1)',
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        fill: true,
      },
    ],
  };

  return (
    <div style={{ padding: '1rem', maxWidth: '700px', margin: 'auto' }}>
      <h2>Predict Stock Prices</h2>
      <form onSubmit={handlePredict}>
        <div style={{ marginBottom: '1rem' }}>
          <label>Company:</label><br />
          <input
            type="text"
            placeholder="e.g. AAPL"
            value={company}
            onChange={(e) => setCompany(e.target.value)}
            required
            style={{ width: '100%', padding: '0.5rem' }}
          />
        </div>
        <div style={{ marginBottom: '1rem' }}>
          <label>Date:</label><br />
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            required
            style={{ width: '100%', padding: '0.5rem' }}
          />
        </div>
        <button type="submit" style={{ padding: '0.5rem 1rem' }}>Get Prediction</button>
      </form>

      {result && (
        <div style={{ marginTop: '1.5rem', backgroundColor: '#f5f5f5', padding: '1rem', borderRadius: '6px' }}>
          <h4 style={{ marginBottom: '1rem' }}>
            <strong>{result.company}</strong> - Predicted vs Actual Prices after <strong>{result.date}</strong>
          </h4>

          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ backgroundColor: '#ddd' }}>
                <th style={{ padding: '8px', border: '1px solid #ccc' }}>Day</th>
                <th style={{ padding: '8px', border: '1px solid #ccc' }}>Predicted Price (₹)</th>
                <th style={{ padding: '8px', border: '1px solid #ccc' }}>Actual Price (₹)</th>
              </tr>
            </thead>
            <tbody>
              {result.predicted_close_prices_next_10_days.map((pred, idx) => (
                <tr key={idx}>
                  <td style={{ padding: '8px', border: '1px solid #ccc' }}>Day {idx + 1}</td>
                  <td style={{ padding: '8px', border: '1px solid #ccc' }}>{pred.toFixed(2)}</td>
                  <td style={{ padding: '8px', border: '1px solid #ccc' }}>
                    {result.actual_close_prices_next_10_days && result.actual_close_prices_next_10_days[idx] !== undefined
                      ? result.actual_close_prices_next_10_days[idx].toFixed(2)
                      : 'N/A'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Chart displaying the data */}
          <div style={{ marginTop: '2rem' }}>
            <Line data={chartData} />
          </div>
        </div>
      )}

      {error && (
        <div style={{ marginTop: '1rem', color: 'red' }}>
          <strong>Error:</strong> {error}
        </div>
      )}
    </div>
  );
};

export default Predictor;
