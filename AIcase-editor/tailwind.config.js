/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: "#00f2ff",
        secondary: "#7000ff",
        accent: "#facc15",
        "editor-bg": "#0a0a0f",
        "editor-sidebar": "#0f0f14",
        "editor-border": "rgba(255, 255, 255, 0.06)",
      },
      animation: {
        'pulse': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
}
