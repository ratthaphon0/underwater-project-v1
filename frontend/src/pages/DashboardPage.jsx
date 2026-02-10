import React from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area 
} from 'recharts';
import { Activity, Droplets, Thermometer, Waves, Camera, AlertTriangle } from 'lucide-react';

const DashboardPage = ({ telemetry }) => {
  // ดึงข้อมูลจาก props telemetry ที่ส่งมาจาก App.jsx
  // สมมติว่าโครงสร้างคือ { data: [...], latest: {...}, status: 'connected' }
  const data = telemetry?.data || [];
  const latest = telemetry?.latest || {};

  return (
    <main className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6">
      
      {/* 1. Status & Overview */}
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <Activity className="text-blue-500" /> Dashboard
        </h2>
        <div className="text-sm bg-green-100 text-green-700 px-3 py-1 rounded-full font-medium">
          Session ID: {latest.session_id ? latest.session_id.slice(0,8) : 'No Active Session'}
        </div>
      </div>

      {/* 2. Real-time Cards (Mapping from water_telemetry) */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard 
          title="Temp (Celsius)" 
          value={`${latest.temperature ?? '--'}°C`} 
          icon={<Thermometer className="text-orange-500" />} 
          color="bg-orange-50 dark:bg-orange-900/20" 
        />
        <StatCard 
          title="pH Level" 
          value={latest.ph ?? '--'} 
          icon={<Droplets className="text-blue-500" />} 
          color="bg-blue-50 dark:bg-blue-900/20" 
        />
        <StatCard 
          title="Dissolved Oxygen" 
          value={`${latest.dissolved_oxygen ?? '--'} mg/L`} 
          icon={<Waves className="text-cyan-500" />} 
          color="bg-cyan-50 dark:bg-cyan-900/20" 
        />
        <StatCard 
          title="Turbidity" 
          value={`${latest.turbidity ?? '--'} NTU`} 
          icon={<Camera className="text-purple-500" />} 
          color="bg-purple-50 dark:bg-purple-900/20" 
        />
      </div>

      {/* 3. Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700">
          <h3 className="font-bold mb-6">Water Quality Trends</h3>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data}>
                <defs>
                  <linearGradient id="colorPh" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="timestamp" hide />
                <YAxis stroke="#94a3b8" fontSize={12} />
                <Tooltip />
                <Area type="monotone" dataKey="ph" stroke="#3b82f6" fillOpacity={1} fill="url(#colorPh)" name="pH Level" />
                <Line type="monotone" dataKey="temperature" stroke="#f59e0b" dot={false} name="Temp" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 4. AI Vision Integration (fish_detections) */}
        <div className="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700">
          <h3 className="font-bold mb-4">AI Detection Results</h3>
          <div className="space-y-4">
            <div className="aspect-video bg-slate-100 dark:bg-slate-900 rounded-lg flex items-center justify-center border-2 border-dashed border-slate-300 dark:border-slate-600 relative overflow-hidden">
               {/* ใส่รูปภาพจาก raw_image_path หรือ enhanced_image_path */}
               <span className="text-slate-400 text-sm">Live Camera Feed</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-slate-50 dark:bg-slate-900/50 rounded-xl">
              <span className="text-sm font-medium">Fish Count</span>
              <span className="text-2xl font-black text-blue-600">12</span>
            </div>
          </div>
        </div>
      </div>

      {/* 5. Alerts based on tilapia_lifecycle_standards */}
      <div className="bg-red-50 dark:bg-red-900/10 border border-red-100 dark:border-red-900/30 p-4 rounded-xl flex gap-3">
        <AlertTriangle className="text-red-500 shrink-0" />
        <div>
          <h4 className="text-red-800 dark:text-red-400 font-bold text-sm">Standard Alert</h4>
          <p className="text-red-700 dark:text-red-300 text-xs">
            Current pH level (6.2) is approaching the minimum threshold (6.0) for Adult Tilapia.
          </p>
        </div>
      </div>

    </main>
  );
};

const StatCard = ({ title, value, icon, color }) => (
  <div className="bg-white dark:bg-slate-800 p-4 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700">
    <div className="flex items-start justify-between">
      <div>
        <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">{title}</p>
        <h3 className="text-2xl font-bold mt-1">{value}</h3>
      </div>
      <div className={`p-2 rounded-xl ${color}`}>
        {icon}
      </div>
    </div>
  </div>
);

export default DashboardPage;
