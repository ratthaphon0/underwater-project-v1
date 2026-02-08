/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#00f2ff", // Electric Cyan (สีหลัก)
        secondary: "#00d1ff",
        accent: "#39ff14", // Neon Green (สี AI)
        "background-light": "#f1f5f9",
        "background-dark": "#0a0f18",
        "panel-dark": "#161e2d",
      },
      fontFamily: {
        display: ["JetBrains Mono", "monospace"],
        sans: ["Inter", "sans-serif"],
      },
      animation: {
        'spin-slow': 'spin 3s linear infinite',
      }
    },
  },
  plugins: [],
}