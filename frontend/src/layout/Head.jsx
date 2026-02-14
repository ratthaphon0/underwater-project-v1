export default function Head() {
    return (
        <div className="flex items-center gap-4 w-full">

            {/* เส้นซ้าย */}
            <div className="flex-1 h-[1px] bg-black rounded-full"></div>

            {/* icon container */}
            <img
                src="/LogoSub_marien.png"
                className="w-11 h-10 brightness-0 contrast-200"
            />

            {/* เส้นขวา */}
            <div className="flex-1 h-[1px] bg-black rounded-full"></div>

        </div>
    )
}
