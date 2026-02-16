import Navbar from "../layout/Navbar.jsx"
import HeadMobile from "../layout/HeadMobile.jsx"
import CardpH from "../components/Home/Dashboad/CardpH.jsx"

export default function HomePage() {
    return (
        <div className="flex flex-col min-h-screen">
            <main className="flex-1 bg-gray-100 p-4">
                <HeadMobile />
                <CardpH />
            </main>
            <Navbar />
        </div>
    )
}