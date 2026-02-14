import Navbar from "../layout/Navbar.jsx"
import Head from "../layout/Head.jsx"

export default function HomePage() {
    return (
        <div className="flex flex-col min-h-screen">
            <main className="flex-1 bg-gray-100 p-4">
                {/* Show head only on mobile */}
                <div className="md:hidden">
                    <Head />
                </div>
            </main>
            <Navbar />
        </div>
    )
}