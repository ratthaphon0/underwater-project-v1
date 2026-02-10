import React from 'react';
import useTelemetry from './hooks/useTelemetry';
import DashboardPage from './pages/DashboardPage';

function App() {
  const telemetry = useTelemetry();

  // 1. ลอง Un-comment บรรทัดข้างล่างนี้เพื่อเช็คว่า React รันขึ้นไหม
  // return <h1 className="text-5xl text-red-500 p-10">Hello React!</h1>

  return (
    <div className="bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100 min-h-screen overflow-hidden flex flex-col font-sans">

      {/* --- MAIN DASHBOARD --- */}
      {/* ส่งข้อมูล telemetry (ที่มี mockData) เข้าไปใน DashboardPage */}
      <DashboardPage telemetry={telemetry} />

    
    </div>
  );
}

export default App;