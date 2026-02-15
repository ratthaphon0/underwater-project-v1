import { Routes, Route } from 'react-router-dom'
import DashboardPage from './pages/DashboardPage'
import HomePage from './pages/Home'

export default function AppRouter() {
    return (
        <Routes>
            {/* Main Routes */}
            <Route path="/" element={<HomePage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
        </Routes>
    )
}