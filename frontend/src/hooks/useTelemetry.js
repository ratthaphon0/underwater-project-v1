import { useState, useEffect } from 'react';

const useTelemetry = () => {
  // สร้างข้อมูลจำลองตามโครงสร้าง DB: water_telemetry
  const mockData = [
    { timestamp: '12:00', ph: 7.2, temperature: 28.5, dissolved_oxygen: 5.5, turbidity: 10, session_id: 'SESS-001' },
    { timestamp: '12:05', ph: 7.1, temperature: 28.7, dissolved_oxygen: 5.3, turbidity: 12, session_id: 'SESS-001' },
    { timestamp: '12:10', ph: 7.3, temperature: 28.4, dissolved_oxygen: 5.8, turbidity: 11, session_id: 'SESS-001' },
    { timestamp: '12:15', ph: 6.9, temperature: 29.0, dissolved_oxygen: 4.9, turbidity: 15, session_id: 'SESS-001' },
    { timestamp: '12:20', ph: 7.0, temperature: 28.8, dissolved_oxygen: 5.1, turbidity: 13, session_id: 'SESS-001' },
  ];

  const [data, setData] = useState(mockData);
  const [latest, setLatest] = useState(mockData[mockData.length - 1]);
  const [status, setStatus] = useState('online (mock)');

  // จำลองว่ามีการอัปเดตข้อมูลทุกๆ 5 วินาที
  useEffect(() => {
    const interval = setInterval(() => {
      console.log("Mock data is running...");
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return { data, latest, status };
};

export default useTelemetry;