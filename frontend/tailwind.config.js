/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: '#050505',
        surface: '#0A0A0A',
        border: '#262626',
        accent: {
          DEFAULT: '#CCFF00',
          red: '#FF3366',
          cyan: '#00F0FF',
          yellow: '#FFD600',
        },
        team: {
          a: '#FF6B35',
          b: '#00B4D8',
        }
      },
      fontFamily: {
        syne: ['Syne', 'sans-serif'],
        mono: ['Space Mono', 'monospace'],
      },
      borderRadius: {
        DEFAULT: '0',
        none: '0',
        sm: '0',
        md: '0',
        lg: '0',
        xl: '0',
      },
    },
  },
  plugins: [],
};
