import { useState, useEffect } from 'react';

function App() {
  // จำลอง State ข้อมูล (เดี๋ยวเราจะต่อกับ Backend จริงทีหลัง)
  const [telemetry, setTelemetry] = useState({
    depth: 3.56,
    temp: 18.4,
    heading: 45,
    battery: 88,
    ph: 6.5,
    status: "NOMINAL"
  });

  // ตัวอย่างฟังก์ชันดึงข้อมูล (Mock)
  useEffect(() => {
    const interval = setInterval(() => {
      // จำลองตัวเลขขยับไปมาให้ดูเหมือนจริง
      setTelemetry(prev => ({
        ...prev,
        depth: +(prev.depth + (Math.random() * 0.1 - 0.05)).toFixed(2),
        heading: Math.floor(prev.heading + (Math.random() * 2 - 1)),
      }));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-background-light dark:bg-background-dark text-slate-900 dark:text-slate-100 min-h-screen overflow-hidden flex flex-col font-sans">
      
      {/* --- HEADER --- */}
      <header className="border-b border-slate-200 dark:border-slate-800 bg-white/50 dark:bg-panel-dark/50 backdrop-blur-md px-6 py-3 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <span className="material-icons text-primary text-3xl">scuba_diving</span>
          <div>
            <h1 className="text-lg font-bold uppercase tracking-widest font-display text-primary">
              AquaControl <span className="text-slate-400">v1.0</span>
            </h1>
            <p className="text-[10px] text-slate-500 uppercase tracking-tighter">Remote Deep-Sea Exploration Unit 04</p>
          </div>
        </div>
        
        <div className="flex items-center gap-6">
          <div className="flex flex-col items-end">
            <span className="text-[10px] text-slate-500 uppercase">Signal Strength</span>
            <div className="flex gap-0.5 mt-1">
              {[1, 2, 3].map(i => <div key={i} className="w-1 h-3 bg-primary"></div>)}
              <div className="w-1 h-3 bg-primary/30"></div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-xs font-display text-accent animate-pulse">REC ● 01:24:55</div>
            <div className="text-[10px] text-slate-500">2026-02-08 | UTC</div>
          </div>
        </div>
      </header>

      {/* --- MAIN DASHBOARD --- */}
      <main className="flex-1 grid grid-cols-12 gap-4 p-4">
        
        {/* LEFT PANEL: NAVIGATION */}
        <aside className="col-span-12 lg:col-span-2 flex flex-col gap-4">
          <div className="bg-white dark:bg-panel-dark border border-slate-200 dark:border-slate-800 rounded-xl p-6 flex flex-col items-center justify-center flex-1">
            <h3 className="text-xs uppercase text-slate-500 mb-6 font-display">Heading</h3>
            <div className="relative w-32 h-32 rounded-full border-4 border-slate-200 dark:border-slate-800 flex items-center justify-center">
               {/* Compass UI */}
               <div className="absolute inset-0 flex items-center justify-center">
                 <div className="w-full h-[1px] bg-slate-200 dark:bg-slate-800"></div>
                 <div className="w-[1px] h-full bg-slate-200 dark:bg-slate-800 absolute"></div>
               </div>
               <div className="absolute top-1 text-[10px] font-bold text-primary">N</div>
               <div className="absolute bottom-1 text-[10px] font-bold text-slate-500">S</div>
               <div 
                 className="relative w-24 h-24 rounded-full border border-primary/20 flex items-center justify-center transition-transform duration-500 ease-out"
                 style={{ transform: `rotate(${telemetry.heading}deg)` }}
               >
                 <span className="material-icons text-primary text-2xl rotate-45">navigation</span>
               </div>
               <div className="absolute text-xl font-bold font-display">{telemetry.heading}°</div>
            </div>
          </div>

          <div className="bg-white dark:bg-panel-dark border border-slate-200 dark:border-slate-800 rounded-xl p-4">
            <h3 className="text-xs uppercase text-slate-500 mb-3 font-display">Thruster Status</h3>
            <div className="space-y-3">
              {['T1 (Port)', 'T2 (Starboard)'].map((t, i) => (
                <div key={t}>
                  <div className="flex justify-between items-center text-[10px] mb-1">
                    <span>{t}</span>
                    <span className="text-accent">ACTIVE</span>
                  </div>
                  <div className="w-full h-1 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div className="bg-primary h-full" style={{ width: i === 0 ? '65%' : '62%' }}></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </aside>

        {/* CENTER PANEL: CAMERA FEED */}
        <section className="col-span-12 lg:col-span-8 flex flex-col gap-4">
          <div className="relative flex-1 bg-black rounded-xl overflow-hidden border-2 border-slate-200 dark:border-slate-800 shadow-2xl min-h-[400px]">
            {/* Placeholder Image (แทนกล้องจริงไปก่อน) */}
            <div className="absolute inset-0 bg-gradient-to-b from-blue-900/40 to-black/80 z-0"></div>
            <div className="scanline z-10"></div>
            
            {/* AI Detection Box Overlay */}
            <div className="absolute top-[35%] left-[30%] w-48 h-32 border-2 border-accent/60 rounded shadow-[0_0_15px_rgba(57,255,20,0.3)] z-20">
              <div className="absolute -top-6 left-0 bg-accent text-black text-[10px] font-bold px-1 py-0.5 rounded-sm">
                TARGET: NILE TILAPIA (94.2%)
              </div>
              {/* Corner Markers */}
              <div className="absolute -bottom-1 -right-1 w-4 h-4 border-b-2 border-r-2 border-accent"></div>
              <div className="absolute -top-1 -left-1 w-4 h-4 border-t-2 border-l-2 border-accent"></div>
            </div>

            {/* OSD (On Screen Display) */}
            <div className="absolute top-4 left-4 font-display text-[12px] text-white flex flex-col gap-1 z-30">
              <div className="bg-black/50 px-2 py-1 border-l-2 border-primary">ALT: 12.4m</div>
              <div className="bg-black/50 px-2 py-1 border-l-2 border-primary">SPD: 1.2 kn</div>
              <div className="bg-black/50 px-2 py-1 border-l-2 border-primary">BAT: {telemetry.battery}%</div>
            </div>
            
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-30">
               <div className="w-8 h-[1px] bg-white"></div>
               <div className="w-[1px] h-8 bg-white absolute"></div>
               <div className="w-32 h-32 border border-white/20 rounded-full"></div>
            </div>
          </div>

          {/* CONTROLS */}
          <div className="bg-white dark:bg-panel-dark border border-slate-200 dark:border-slate-800 rounded-xl p-4 flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="grid grid-cols-3 gap-1">
                <div></div>
                <button className="btn-control"><span className="material-icons">arrow_upward</span></button>
                <div></div>
                <button className="btn-control"><span className="material-icons">arrow_back</span></button>
                <button className="btn-control"><span className="material-icons">arrow_downward</span></button>
                <button className="btn-control"><span className="material-icons">arrow_forward</span></button>
              </div>
              <div className="h-16 w-[1px] bg-slate-200 dark:bg-slate-800 hidden sm:block"></div>
              <div className="flex flex-col gap-2">
                <button className="px-4 py-2 rounded bg-slate-100 dark:bg-slate-800 hover:bg-primary/20 flex items-center gap-2 border border-slate-200 dark:border-slate-700 transition-colors">
                  <span className="material-icons text-sm">lightbulb</span>
                  <span className="text-xs font-semibold">FLOOD LIGHTS</span>
                </button>
              </div>
            </div>
            <div className="flex gap-2">
              <button className="bg-red-500/20 border border-red-500/50 text-red-500 px-6 py-4 rounded font-bold hover:bg-red-500 hover:text-white transition-all uppercase tracking-widest text-sm">
                Emergency Surface
              </button>
            </div>
          </div>
        </section>

        {/* RIGHT PANEL: SENSORS */}
        <aside className="col-span-12 lg:col-span-2 flex flex-col gap-4">
           {/* pH Level */}
           <div className="bg-white dark:bg-panel-dark border border-slate-200 dark:border-slate-800 rounded-xl p-6 flex flex-col items-center justify-center flex-1 hover:border-primary transition-all group cursor-pointer">
              <h3 className="text-xs uppercase text-slate-500 mb-6 font-display">pH Level</h3>
              <div className="relative w-32 h-32 rounded-full border-4 border-slate-200 dark:border-slate-800 flex items-center justify-center group-hover:border-primary/30 transition-all">
                <div className="text-center">
                  <div className="text-3xl font-bold font-display">{telemetry.ph}</div>
                  <div className="text-xs text-slate-500 uppercase">Acidic</div>
                </div>
              </div>
              <span className="mt-4 text-[10px] text-primary group-hover:underline flex items-center gap-1">
                 <span className="material-icons text-[12px]">analytics</span> VIEW HISTORY
              </span>
           </div>

           {/* Depth */}
           <div className="bg-white dark:bg-panel-dark border border-slate-200 dark:border-slate-800 rounded-xl p-6 flex flex-col items-center justify-center flex-1">
              <h3 className="text-xs uppercase text-slate-500 mb-6 font-display">Current Depth</h3>
              <div className="relative w-32 h-32 rounded-full border-4 border-slate-200 dark:border-slate-800 flex items-center justify-center overflow-hidden bg-slate-50 dark:bg-slate-900/50">
                 {/* Water Level Animation */}
                 <div className="absolute bottom-0 left-0 w-full bg-primary/20 transition-all duration-1000" style={{ height: `${(telemetry.depth / 10) * 100}%` }}></div>
                 <div className="text-center z-10">
                    <div className="text-3xl font-bold font-display">{telemetry.depth}<span className="text-sm font-normal text-slate-500">m</span></div>
                    <div className="text-xs text-slate-500 uppercase">DEEP</div>
                 </div>
              </div>
           </div>
        </aside>

      </main>

      {/* --- FOOTER --- */}
      <footer className="bg-slate-100 dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 px-4 py-2 flex justify-between items-center text-[10px] font-display">
         <div className="flex items-center gap-4">
            <div className="flex items-center gap-1">
               <div className="w-2 h-2 rounded-full bg-accent animate-pulse"></div>
               <span className="text-slate-500 uppercase">SYSTEMS {telemetry.status}</span>
            </div>
            <div className="h-3 w-[1px] bg-slate-300 dark:bg-slate-700"></div>
            <span className="text-slate-400">STORAGE: 42.1 GB REMAINING</span>
         </div>
         <div className="flex items-center gap-4">
            <span className="text-slate-500">LATENCY: 48ms</span>
            <div className="flex items-center gap-2 bg-slate-200 dark:bg-slate-800 px-2 py-0.5 rounded">
               <span className="material-icons text-[12px]">wifi</span>
               <span>COMMS: SECURE</span>
            </div>
         </div>
      </footer>
      
      {/* CSS Utility for button (ใส่ไว้ใน JSX เลยจะได้ไม่ต้องแก้ไฟล์อื่น) */}
      <style>{`
        .btn-control {
          @apply w-10 h-10 rounded bg-slate-100 dark:bg-slate-800 hover:bg-primary/20 flex items-center justify-center transition-all border border-slate-200 dark:border-slate-700 active:scale-95;
        }
      `}</style>
    </div>
  );
}

export default App;