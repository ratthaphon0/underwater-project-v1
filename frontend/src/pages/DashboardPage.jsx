import React, { useState, useEffect } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area 
} from 'recharts';
import { Activity, Droplets, Thermometer, Waves, Camera, MapPin, AlertTriangle } from 'lucide-react';

const Dashboard = () => {
  // สมมติสถานะข้อมูล (ในงานจริงจะใช้ useEffect ดึงจาก API)
  const [telemetry, setTelemetry] = useState([]);
  const [session, setSession] = useState({ location_name: 'ลุ่มแม่น้ำเจ้าพระยา', status: 'Active' });
  const [fishStats, setFishStats] = useState({ total: 0, healthy: 0, warning: 0 });

  // Mock Data สำหรับแสดงผลกราฟ
  const mockData = [
    { time: '10:00', temp: 28.5, ph: 7.2, do: 5.4, fish: 12 },
    { time: '10:05', temp: 28.7, ph: 7.1, do: 5.2, fish: 8 },
    { time: '10:10', temp: 29.1, ph: 6.9, do: 4.8, fish: 15 },
    { time: '10:15', temp: 28.9, ph: 7.0, do: 5.0, fish: 22 },
  ];

  return (
    <div className="p-6 bg-slate-50 min-h-screen font-sans">
      {/* Header Section */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Water Quality Monitoring</h1>
          <p className="text-slate-500 flex items-center gap-1">
            <MapPin size={16} /> Location: {session.location_name}
          </p>
        </div>
        <div className="flex gap-3">
          <span className="px-4 py-2 bg-blue-100 text-blue-700 rounded-full text-sm font-semibold flex items-center gap-2">
            <Activity size={16} /> Session: Running
          </span>
        </div>
      </div>

      {/* Stats Cards (KPIs) */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard title="Temperature" value="28.5°C" icon={<Thermometer className="text-orange-500" />} color="bg-orange-50" />
        <StatCard title="pH Level" value="7.2" icon={<Droplets className="text-blue-500" />} color="bg-blue-50" />
        <StatCard title="Dissolved Oxygen" value="5.4 mg/L" icon={<Waves className="text-cyan-500" />} color="bg-cyan-50" />
        <StatCard title="Fish Count (AI)" value="57" icon={<Camera className="text-purple-500" />} color="bg-purple-50" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Main Chart - Water Quality Trends */}
        <div className="lg:col-span-2 bg-white p-6 rounded-xl shadow-sm border border-slate-100">
          <h3 className="text-lg font-bold mb-4 text-slate-700">Water Telemetry Trends</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={mockData}>
                <defs>
                  <linearGradient id="colorDo" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.1}/>
                    <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="time" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip />
                <Area type="monotone" dataKey="do" stroke="#06b6d4" fillOpacity={1} fill="url(#colorDo)" name="Oxygen (DO)" />
                <Line type="monotone" dataKey="temp" stroke="#f59e0b" name="Temp" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* AI Fish Detection & Health Status */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
          <h3 className="text-lg font-bold mb-4 text-slate-700">AI Vision Results</h3>
          <div className="space-y-4">
            <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-slate-600">Health Status</span>
                <span className="text-xs px-2 py-1 bg-green-100 text-green-700 rounded text-bold uppercase">Optimal</span>
              </div>
              <p className="text-2xl font-bold text-slate-800 underline decoration-green-400">Normal</p>
            </div>

            <div className="mt-6">
              <h4 className="text-sm font-semibold text-slate-500 mb-3">Recent Detections</h4>
              {/* ส่วนนี้ Map ข้อมูลจาก fish_detections */}
              {[1, 2].map((i) => (
                <div key={i} className="flex gap-3 items-center mb-3 p-2 hover:bg-slate-50 rounded-lg transition-colors cursor-pointer border border-transparent hover:border-slate-200">
                  <div className="w-16 h-12 bg-slate-200 rounded overflow-hidden">
                     {/* ตรงนี้จะแสดง raw_image_path หรือ enhanced_image_path */}
                     <div className="w-full h-full bg-slate-300 flex items-center justify-center"><Camera size={14} /></div>
                  </div>
                  <div>
                    <p className="text-sm font-bold">Tilapia Detected ({i*4} qty)</p>
                    <p className="text-xs text-slate-400">10:15:32 AM</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

      </div>

      {/* Alert Section from predictions/standards */}
      <div className="mt-6 p-4 bg-amber-50 border border-amber-200 rounded-lg flex items-start gap-3">
        <AlertTriangle className="text-amber-600 shrink-0" />
        <div>
          <h4 className="text-amber-800 font-bold text-sm">Prediction Alert</h4>
          <p className="text-amber-700 text-xs">
            Based on current trends, Dissolved Oxygen (DO) might drop below 3.0 mg/L (Standard threshold for Adult Tilapia) within the next 2 hours.
          </p>
        </div>
      </div>
    </div>
  );
};

const StatCard = ({ title, value, icon, color }) => (
  <div className={`p-5 rounded-xl border border-slate-100 shadow-sm bg-white`}>
    <div className="flex justify-between items-start">
      <div>
        <p className="text-sm font-medium text-slate-500 mb-1">{title}</p>
        <h2 className="text-2xl font-bold text-slate-800">{value}</h2>
      </div>
      <div className={`p-2 rounded-lg ${color}`}>
        {icon}
      </div>
    </div>
  </div>
);

export default Dashboard;