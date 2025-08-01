import { useState } from 'react';
import axios from 'axios';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, BarElement, CategoryScale, LinearScale, Title } from 'chart.js';

ChartJS.register(BarElement, CategoryScale, LinearScale, Title);

export default function Home() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');
  const [chartData, setChartData] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleManualUpload = async () => {
    if (!file) {
      setMessage('Please select a file');
      return;
    }
    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await axios.post('http://localhost:8000/process-sales', formData);
      setMessage(response.data.message);
      fetchMetrics();
    } catch (error) {
      setMessage('Error processing file');
    }
  };

  const handleGoogleFetch = async () => {
    try {
      const response = await axios.post('http://localhost:8000/fetch-and-process');
      setMessage(response.data.message);
      fetchMetrics();
    } catch (error) {
      setMessage('Error fetching Google data');
    }
  };

  const fetchMetrics = async () => {
    try {
      const response = await axios.get('http://localhost:8000/metrics');
      setChartData({
        labels: response.data.labels,
        datasets: [{
          label: 'Total Sales ($)',
          data: response.data.values,
          backgroundColor: ['#4CAF50', '#2196F3', '#FF9800'],
          borderColor: ['#388E3C', '#1976D2', '#F57C00'],
          borderWidth: 1
        }]
      });
    } catch (error) {
      setMessage('Error fetching metrics');
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">WMS Dashboard</h1>
      <div className="mb-4">
        <input type="file" accept=".csv,.xlsx" onChange={handleFileChange} className="mb-2" />
        <button
          onClick={handleManualUpload}
          className="bg-blue-500 text-white px-4 py-2 rounded mr-2"
        >
          Upload Sales Data
        </button>
        <button
          onClick={handleGoogleFetch}
          className="bg-green-500 text-white px-4 py-2 rounded"
        >
          Fetch from Google
        </button>
      </div>
      <p>{message}</p>
      {chartData && (
        <Bar
          data={chartData}
          options={{
            scales: {
              y: { beginAtZero: true, title: { display: true, text: 'Sales ($)' } },
              x: { title: { display: true, text: 'MSKU' } }
            }
          }}
        />
      )}
    </div>
  );
}