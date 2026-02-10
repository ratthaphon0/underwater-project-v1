import useTelemetry from './hooks/useTelemetry';
import Header from './layout/Header';
import Footer from './layout/Footer';
import DashboardPage from './pages/DashboardPage';

function App() {
  const telemetry = useTelemetry();

  return (
    <div className="bg-background-light dark:bg-background-dark text-slate-900 dark:text-slate-100 min-h-screen overflow-hidden flex flex-col font-sans">

      {/* --- HEADER --- */}
      <Header />

      {/* --- MAIN DASHBOARD --- */}
      <DashboardPage telemetry={telemetry} />

      {/* --- FOOTER --- */}
      <Footer status={telemetry.status} />

    </div>
  );
}

export default App;