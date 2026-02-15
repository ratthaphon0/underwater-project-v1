export default function Head() {
    return (
        <div className="md:hidden flex items-center gap-4 w-full">

            {/* เส้นซ้าย */}
            <div className="flex-1 h-[2px] bg-black rounded-full"></div>

            {/* icon container */}
            <img
                src="/LogoSub_marien.png"
                className="w-13 h-11 brightness-0 contrast-200"
            />

            {/* เส้นขวา */}
            <div className="flex-1 h-[2px] bg-black rounded-full"></div>

        </div>
    )
}
