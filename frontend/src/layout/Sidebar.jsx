import React from 'react';
import { Home, Settings, PieChart, LineChart as GraphIcon, Ship } from 'lucide-react';

const Sidebar = () => {
  return (
    <aside className="hidden md:flex w-64 bg-[#101e42] flex-col justify-between py-6 px-4 shadow-xl z-20 h-screen sticky top-0">
        <div>
            {/* Logo Area */}
            <div className="flex items-center gap-3 mb-10 px-2">
                <div className="bg-white/10 p-2 rounded-xl">
                    <Ship className="w-8 h-8 text-white" strokeWidth={1.5} />
                </div>
                <div>
                    <h1 className="text-white font-bold tracking-wider text-lg">AQUA NAV</h1>
                    <p className="text-xs text-gray-400">Control Center</p>
                </div>
            </div>

            {/* Menu Items */}
            <nav className="space-y-2">
                <DesktopNavItem icon={<Home size={20} />} label="Overview" />
                <DesktopNavItem icon={<PieChart size={20} />} label="Dashboard" active />
                <DesktopNavItem icon={<GraphIcon size={20} />} label="Analytics" />
                <DesktopNavItem icon={<Settings size={20} />} label="Settings" />
            </nav>
        </div>

        {/* Footer Sidebar */}
        <div className="bg-[#1a2b55] rounded-xl p-4">
            <p className="text-xs text-gray-400 mb-1">System Status</p>
            <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-white text-sm font-medium">Online</span>
            </div>
        </div>
    </aside>
  );
};

// Sub-component ย่อยของ Sidebar
const DesktopNavItem = ({ icon, label, active }) => (
    <button className={`flex items-center gap-3 w-full px-4 py-3 rounded-xl transition-all ${
        active 
        ? 'bg-[#4fbcdb] text-white shadow-lg shadow-[#4fbcdb]/20' 
        : 'text-gray-400 hover:bg-white/5 hover:text-white'
    }`}>
        {icon}
        <span className="font-medium text-sm">{label}</span>
    </button>
);

export default Sidebar;