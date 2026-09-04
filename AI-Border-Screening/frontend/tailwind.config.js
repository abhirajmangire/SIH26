/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          navy: '#0B1F3A',
          royal: '#1769E0',
          cyan: '#00A8E8',
        },
        status: {
          green: '#16A34A',
          amber: '#F59E0B',
          red: '#DC2626',
        },
        neutral: {
          bg: '#F5F8FC',
          card: '#FFFFFF',
          text: '#172033',
          'text-secondary': '#64748B',
          border: '#E2E8F0',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      boxShadow: {
        'card': '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
        'card-hover': '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
      },
      borderRadius: {
        'card': '8px',
      },
    },
  },
  plugins: [],
}