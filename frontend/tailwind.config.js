/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50:  '#edfaf6',
          100: '#d1f4e9',
          400: '#34d399',
          500: '#10b981',
          600: '#059669',
        },
        surface: {
          900: '#0f0f1a',
          800: '#1a1a2e',
          700: '#16213e',
          600: '#1e2a45',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
}
