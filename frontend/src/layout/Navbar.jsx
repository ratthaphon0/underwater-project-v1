import React, { useState } from 'react'
import { Home, ChartPie, Settings, ChartLine, MapPinned } from 'lucide-react'

const navItems = [
    { name: 'Home', icon: Home, href: '/' },
    { name: 'Dashboard', icon: ChartPie, href: '/dashboard' },
    { name: 'History', icon: ChartLine, href: '/history' },
    { name: 'Map', icon: MapPinned, href: '/map' },
    { name: 'Setting', icon: Settings, href: '/setting' },

]

// Reusable Button Component
function NavButton({ item, activeTab, setActiveTab, variant = 'mobile' }) {
    const { name, icon: Icon } = item
    const isActive = activeTab === name

    if (variant === 'desktop') {
        return (
            <button
                onClick={() => setActiveTab(name)}
                className={`
          flex items-center gap-4 w-full px-4 py-3.5 rounded-2xl
          transition-all duration-200 group
          ${isActive
                        ? 'bg-blue-600/10 text-blue-500'
                        : 'hover:bg-gray-800 text-gray-400 hover:text-white'
                    }
        `}
            >
                <Icon
                    size={22}
                    className={isActive ? 'text-blue-500' : 'group-hover:text-blue-400'}
                />

                <span className="text-sm font-semibold">{name}</span>

                {isActive && (
                    <div className="ml-auto w-1.5 h-1.5 bg-blue-500 rounded-full shadow-[0_0_8px_rgba(59,130,246,1)]" />
                )}
            </button>
        )
    }

    // Mobile version
    return (
        <button
            onClick={() => setActiveTab(name)}
            className="relative flex flex-col items-center justify-center w-full h-full transition-all duration-300"
        >
            {/* Active circle */}
            <div
                className={`
          absolute -top-6 transition-all duration-500 ease-out
          ${isActive ? 'scale-100 opacity-100' : 'scale-0 opacity-0'}
        `}
            >
                <div className="bg-blue-600 p-3 rounded-full shadow-lg border-[7px] border-gray-900">
                    <Icon size={24} className="text-white" />
                </div>
            </div>
            {isActive && (
                <span className="absolute bottom-4 text-[12px] font-bold text-white uppercase tracking-wider">
                    {name}
                </span>)}

            {/* Default icon */}
            <div
                className={`
          flex flex-col items-center transition-all duration-300
          ${isActive ? 'translate-y-6 opacity-0' : ''}
        `}
            >
                <Icon size={22} className="text-gray-400" />

            </div>



        </button>
    )
}

export default function Navbar() {
    const [activeTab, setActiveTab] = useState('Home')

    return (
        <>
            {/* Mobile Navbar */}
            <nav className="md:hidden fixed bottom-0 left-0 right-0 h-20 bg-gray-900 border-t border-gray-800 z-50 px-2 pb-safe">
                <div className="flex justify-around items-center h-full">
                    {navItems.map((item) => (
                        <NavButton
                            key={item.name}
                            item={item}
                            activeTab={activeTab}
                            setActiveTab={setActiveTab}
                        />
                    ))}
                </div>
            </nav>

            {/* Desktop Sidebar */}
            <nav className="hidden md:flex fixed top-0 left-0 h-screen w-64 bg-gray-900 border-r border-gray-800 text-gray-300 flex-col py-8 z-50">
                {/* Logo */}
                <div className="px-6 mb-10 flex flex-col items-center gap-2">
                    <img
                        src="/LogoSub_marien.png"
                        alt="Logo"
                        className="w-13 h-11"
                    />
                    <div className="text-white font-bold text-xl">
                        CHONLAMART
                    </div>
                </div>

                {/* Menu */}
                <div className="flex flex-col w-full px-4 gap-2">
                    {navItems.map((item) => (
                        <NavButton
                            key={item.name}
                            item={item}
                            activeTab={activeTab}
                            setActiveTab={setActiveTab}
                            variant="desktop"
                        />
                    ))}
                </div>
            </nav>
        </>
    )
}