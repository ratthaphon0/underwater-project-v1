import Navbar from "./layout/Navbar"
import { Routes, Route } from "react-router-dom"
import HomePage from "./pages/Home"
import DashboardPage from "./pages/DashboardPage"

function Router() {
    return (
        <div className="min-h-screen bg-[#0f172a]">

            {/* Sidebar */}
            <Navbar />

            {/* Content wrapper */}
            <div className="md:ml-64">

                {/* Main content */}
                <main className="min-h-screen p-6">
                    <Routes>
                        <Route path="/" element={<HomePage />} />
                        <Route path="/dashboard" element={<DashboardPage />} />
                    </Routes>
                </main>

            </div>

        </div>
    )
}

export default Router