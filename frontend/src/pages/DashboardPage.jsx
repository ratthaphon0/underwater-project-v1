import React from 'react';
import { AreaChart, Area, ResponsiveContainer } from 'recharts';
import { Thermometer, Droplets, Waves, Wind, Activity, PieChart, Ship } from 'lucide-react';

// --- Imports Components ---
import Sidebar from '../layout/Sidebar';       // Desktop Sidebar
import Navbar from '../layout/Navbar';         // Mobile Bottom Nav (อันเดิมที่คุณมี)
import MetricCard from '../components/MetricCard'; // Card Component

const DashboardPage = ({ telemetry }) => {
    const data = telemetry?.data || [
        { name: '1', value: 40 }, { name: '2', value: 30 },
        { name: '3', value: 20 }, { name: '4', value: 27 },
        { name: '5', value: 18 }, { name: '6', value: 23 },
        { name: '7', value: 34 },
    ];
    const latest = telemetry?.latest || {};

    return (
        <div className="min-h-screen bg-[#eef1f5] flex font-sans overflow-hidden">

            {/* 1. เรียกใช้ Sidebar (จะแสดงเฉพาะจอ Desktop เพราะเราใส่ hidden md:flex ไว้ในไฟล์ Sidebar แล้ว) */}
            <Sidebar />

            {/* 2. Main Content */}
            <div className="flex-1 flex flex-col h-screen relative overflow-hidden">

                {/* Mobile Header */}
                <header className="md:hidden pt-8 pb-4 px-6 bg-white z-10 shadow-sm">
                    {/* ... Code Header Mobile เดิม ... */}
                    <div className="flex flex-col items-center justify-center mt-2">
                        <div className="flex items-center gap-2">
                            <PieChart className="w-5 h-5 text-gray-800" />
                            <h1 className="text-lg font-black tracking-wider text-gray-800 uppercase">Dash Board</h1>
                        </div>
                    </div>
                </header>

                {/* Desktop Header */}
                <header className="hidden md:flex justify-between items-center px-8 py-5 bg-white shadow-sm z-10">
                    <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
                        <Activity className="text-[#4fbcdb]" /> Real-time Telemetry
                    </h2>
                    {/* User Profile etc. */}
                </header>

                {/* Scrollable Body */}
                <main className="flex-1 overflow-y-auto p-5 md:p-8 pb-24 md:pb-8 hide-scrollbar">
                    <div className="max-w-7xl mx-auto space-y-6">

                        {/* Graph Section */}
                        <div className="flex flex-col lg:flex-row gap-4 lg:h-80">
                            <div className="flex-1 bg-[#6c7285] rounded-3xl p-6 relative shadow-lg overflow-hidden h-48 lg:h-full">
                                <ResponsiveContainer width="100%" height="100%">
                                    <AreaChart data={data}>
                                        <defs>
                                            <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#ffffff" stopOpacity={0.3} />
                                                <stop offset="95%" stopColor="#ffffff" stopOpacity={0} />
                                            </linearGradient>
                                        </defs>
                                        <Area type="monotone" dataKey="value" stroke="#ffffff" strokeWidth={3} fill="url(#colorValue)" />
                                    </AreaChart>
                                </ResponsiveContainer>
                                <div className="absolute top-6 right-6 text-white/50">
                                    <Activity size={24} />
                                </div>
                            </div>
                            {/* Side Control for Desktop */}
                            <div className="hidden lg:flex w-24 bg-white rounded-3xl flex-col items-center justify-between py-6 shadow-sm">
                                <div className="space-y-4 flex flex-col items-center">
                                    <div className="p-3 bg-gray-100 rounded-full text-gray-500"><Wind size={20} /></div>
                                    <div className="p-3 bg-gray-100 rounded-full text-gray-500"><Waves size={20} /></div>
                                </div>
                                <div className="bg-[#101e42] p-4 rounded-full shadow-lg cursor-pointer hover:scale-110 transition-transform">
                                    <Ship className="w-6 h-6 text-white" />
                                </div>
                            </div>
                        </div>

                        {/* Metrics Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                            <MetricCard
                                label="TEMP (CELSIUS)"
                                value={latest.temperature ? `${latest.temperature}°C` : '-- °C'}
                                icon={<Thermometer className="w-6 h-6 text-gray-600" />}
                            />
                            <MetricCard
                                label="pH LEVEL"
                                value={latest.ph ?? '--'}
                                icon={<Droplets className="w-6 h-6 text-gray-600" />}
                            />
                            <MetricCard
                                label="DISSOLVED OXYGEN"
                                value={latest.dissolved_oxygen ? `${latest.dissolved_oxygen} mg/L` : '-- mg/L'}
                                icon={<Wind className="w-6 h-6 text-gray-600" />}
                            />
                            <MetricCard
                                label="TURBIDITY"
                                value={latest.turbidity ? `${latest.turbidity} NTU` : '-- NTU'}
                                icon={<Waves className="w-6 h-6 text-gray-600" />}
                            />
                        </div>
                    </div>
                </main>

                {/* 3. เรียกใช้ Navbar (Mobile Bottom Nav) */}
                {/* ในไฟล์ Navbar.jsx อย่าลืมใส่ className="md:hidden ..." ไว้นะครับ จะได้ซ่อนตอนจอใหญ่ */}
                <Navbar />

            </div>
        </div>
    );
};

export default DashboardPage;
