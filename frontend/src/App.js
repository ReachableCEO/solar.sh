import React, { useState } from 'react';

function App() {
  const [projectId, setProjectId] = useState('');
  const [checkoutUrl, setCheckoutUrl] = useState('');
  const [pdfUrl, setPdfUrl] = useState('');

  const handleCalculate = async () => {
    const response = await fetch('/api/calculate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        project_name: 'Ground Mount Project 1',
        location: { lat: 35.79, lon: -78.78 },
        lidar_data: 'dummy_lidar_data',
      }),
    });
    const data = await response.json();
    setProjectId(data.project_id);
  };

  const handleCheckout = async () => {
    const response = await fetch('/api/checkout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project_id: projectId }),
    });
    const data = await response.json();
    setCheckoutUrl(data.checkout_url);
  };

  const handleDownload = () => {
    setPdfUrl(`/api/download/${projectId}`);
  };

  return (
    <div>
      <h1>Sol-Calc</h1>
      <button onClick={handleCalculate}>Calculate</button>
      {projectId && <p>Project ID: {projectId}</p>}
      {projectId && <button onClick={handleCheckout}>Checkout</button>}
      {checkoutUrl && <p>Checkout URL: <a href={checkoutUrl}>{checkoutUrl}</a></p>}
      {checkoutUrl && <button onClick={handleDownload}>Download PDF</button>}
      {pdfUrl && <p>PDF URL: <a href={pdfUrl}>{pdfUrl}</a></p>}
    </div>
  );
}

export default App;
