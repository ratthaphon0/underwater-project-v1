// 1. ส่วน Import: ต้องอยู่บนสุดของไฟล์
import React, { useState, useEffect } from 'react';

// ชื่อ Component (ตรงกับชื่อไฟล์)
const Compass = () => {
    // 2. ส่วน Logic (Hooks): ประกาศตัวแปรและฟังก์ชันทำงานที่นี่ ก่อน return
    const [heading, setHeading] = useState(0);

    useEffect(() => {
        const handleOrientation = (e) => {
            let compass = e.webkitCompassHeading || Math.abs(e.alpha - 360);
            setHeading(compass);
        };

        // ฟังก์ชันสำหรับขออนุญาตใช้งาน Sensor (จำเป็นสำหรับ iOS 13+)
        const requestAccess = () => {
            if (typeof DeviceOrientationEvent !== 'undefined' &&
                typeof DeviceOrientationEvent.requestPermission === 'function') {
                DeviceOrientationEvent.requestPermission()
                    .then((response) => {
                        if (response === 'granted') {
                            window.addEventListener('deviceorientation', handleOrientation);
                        }
                    })
                    .catch(console.error);
            } else {
                // สำหรับ Android และอุปกรณ์อื่นๆ
                window.addEventListener('deviceorientation', handleOrientation);
            }
        };

        requestAccess(); // เรียกทำงานทันที (บาง Browser อาจต้องรอให้กดปุ่มก่อน)

        return () => {
            window.removeEventListener('deviceorientation', handleOrientation);
        };
    }, []);

    // 3. ส่วนแสดงผล (JSX): คือส่วนที่คุณส่งโค้ดมา
    // ผมเพิ่ม style transform เพื่อให้เข็มหมุนตามค่า heading
    return (
        <div
            className="
        fixed
        left-1/2
        bottom-[8%]
        -translate-x-1/2
        w-[clamp(120px,18vw,220px)]
        aspect-square
        rounded-full
        bg-[radial-gradient(circle_at_center,#0f2f2f_0%,#071a1a_70%,#020909_100%)]
        border
        border-emerald-300/60
        shadow-[0_0_25px_rgba(0,255,200,0.35)]
        z-50
      "
        >
            {/* Container สำหรับหมุนเข็มทิศ */}
            <div
                style={{ transform: `rotate(${-heading}deg)` }}
                className="relative w-full h-full transition-transform duration-300 ease-out"
            >

                {/* วงใน */}
                <div
                    className="
            absolute
            inset-[8%]
            rounded-full
            border
            border-dashed
            border-emerald-300/40
            animate-[spin_6s_linear_infinite]
          "
                ></div>

                {/* เข็ม */}
                <div
                    className="
            absolute
            left-1/2
            top-[10%]
            -translate-x-1/2
            w-[2px]
            h-[45%]
            bg-gradient-to-t
            from-transparent
            to-emerald-300
            shadow-[0_0_10px_#00ffd0]
          "
                ></div>

                {/* ตัวอักษร N */}
                <div
                    className="
            absolute
            top-[6%]
            left-1/2
            -translate-x-1/2
            font-mono
            text-[clamp(14px,2vw,18px)]
            text-emerald-200
            drop-shadow-[0_0_6px_rgba(0,255,200,0.8)]
          "
                >
                    N
                </div>
            </div>

            {/* หมายเหตุ: บน iOS บางครั้งอาจต้องมีปุ่มกดเพื่อเริ่มใช้งาน Sensor 
         ถ้าเข็มไม่หมุน อาจต้องสร้างปุ่มใสๆ มาครอบเพื่อเรียก requestAccess() อีกทีครับ
      */}

        </div>
    );
};

export default Compass;