import { useState } from 'react';
import { Droplets } from 'lucide-react';

const EnvironmentBar = () => {
    const [ph, setPh] = useState(7.5);
    const [temp, setTemp] = useState(25.7);
    const [quality, setQuality] = useState('GOOD');
    return (
        <div className="md:hidden flex justify-center w-full mt-4">
            <div className="flex items-center justify-center gap-2 px-4 py-3 bg-[#2D3E61]/20 rounded-full inline-flex">
                {/* pH Section */}
                <div className="flex items-center gap-1 border-r border-gray-400/30 pr-3">
                    <div className="w-5 h-5 flex items-center justify-center">
                        {/* Drop Icon */}
                        <span className="text-white text-xs"><svg xmlns="http://www.w3.org/2000/svg" width={24} height={24} viewBox="0 0 24 24"><path fill="currentColor" d="M9 21.95q-3.05-.35-5.025-2.625T2 13.8q0-2.5 1.988-5.437T10 2q4.025 3.425 6.013 6.363T18 13.8v.2h-2v-.2q0-1.825-1.513-4.125T10 4.65Q7.025 7.375 5.513 9.675T4 13.8q0 2.425 1.4 4.1T9 19.925zm2 .05v-6h3.5q.6 0 1.05.45T16 17.5v1q0 .6-.45 1.05T14.5 20h-2v2zm6 0v-6h1.5v2h2v-2H22v6h-1.5v-2.5h-2V22zm-4.5-3.5h2v-1h-2z"></path></svg></span>
                    </div>

                    <span className="text-sm font-black text-white ml-1">{ph}</span>
                </div>

                {/* Temp Section */}
                <div className="flex items-center gap-1 border-r border-gray-400/30 pr-3 pl-1">
                    <div className="w-5 h-5 flex items-center justify-center">
                        {/* Thermometer Icon */}
                        <span className="text-white"><svg xmlns="http://www.w3.org/2000/svg" width={24} height={24} viewBox="0 0 32 32"><path fill="currentColor" d="M17.5 19.508V8.626h-4v10.88c-1.403.728-2.374 2.18-2.374 3.87a4.376 4.376 0 0 0 8.751.001c0-1.69-.97-3.142-2.376-3.868zm3-14.26c0-2.756-2.244-5-5-5s-5 2.245-5 5v12.727a7.3 7.3 0 0 0-2.375 5.4c0 4.066 3.31 7.377 7.376 7.377s7.375-3.31 7.375-7.377c0-2.086-.878-4.03-2.375-5.402V5.25zm.375 18.13A5.38 5.38 0 0 1 15.5 28.75a5.38 5.38 0 0 1-5.373-5.373c0-1.795.896-3.443 2.376-4.438V5.25c0-1.653 1.343-3 2.997-3s3 1.346 3 3v13.69a5.33 5.33 0 0 1 2.375 4.437zm1.21-14.752l4.5 2.598V6.03z"></path></svg></span>
                    </div>
                    <span className="text-sm font-black text-white">{temp} C°</span>
                </div>

                {/* Quality Section */}
                <div className="flex items-center gap-1 pl-1">
                    <div className="w-5 h-5 flex items-center justify-center">
                        {/* Water Quality Icon */}
                        <div className="text-white"><Droplets size={24} /></div>
                    </div>
                    <span className="text-sm font-black text-[#FFFF]">{quality}</span>
                </div>
            </div>
        </div>

    );
};

export default EnvironmentBar;