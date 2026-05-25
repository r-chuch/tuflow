/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["'Noto Sans TC'", "sans-serif"],
        serif: ["'Fraunces'", "serif"],
        mono: ["'DM Mono'", "monospace"],
      },
      colors: {
        bg: "#0d1210",
        surface: "#141a15",
        surface2: "#1b241c",
        surface3: "#222e23",
        border: "#28352a",
        "border-hi": "#3a4f3c",
        green: "#4ade80",
        "green-soft": "#38c068",
        "green-dim": "#254d35",
        amber: "#fbbf24",
        "amber-dim": "#5c3608",
        blue: "#60a5fa",
        text: "#deeadf",
        "text-hi": "#ecf4ed",
        muted: "#5e7360",
        muted2: "#7a9b7d",
        danger: "#f87171",
      },
    },
  },
  plugins: [],
}
