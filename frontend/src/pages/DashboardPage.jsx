import Navbar from "../layout/Navbar.jsx"

export default function DashboardPage() {
    return (
        <div className="flex flex-col min-h-screen">
            <main className="flex-1 bg-gray-100 p-4">
                <h1 className="text-xl font-bold">Dashboard</h1>
            </main>

            <Navbar />
        </div>
    )
}
