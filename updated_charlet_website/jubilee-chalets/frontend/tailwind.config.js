/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          white: '#FFFFFF',
          black: '#111111',
          'dark-green': '#123D2A',
          'forest-green': '#0B2B1E',
          'light-green': '#E8F0EA',
          'light-grey': '#F5F6F4',
        },
        green: {
          50: '#E8F0EA',
          100: '#d0e2d5',
          200: '#a2c5aa',
          300: '#73a880',
          400: '#458b56',
          500: '#2a6e3f',
          600: '#1e5530',
          700: '#123D2A',
          800: '#0B2B1E',
          900: '#061a12',
        },
      },
      fontFamily: {
        display: ['"Playfair Display"', 'Georgia', 'serif'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.5s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
      backgroundImage: {
        'hero-overlay': 'linear-gradient(to bottom, rgba(11,43,30,0.5) 0%, rgba(11,43,30,0.3) 50%, rgba(11,43,30,0.6) 100%)',
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
    },
  },
  plugins: [
    // @tailwindcss/forms and typography imported conditionally
  ],
}
