/** @type {import('tailwindcss').Config} */
export default {
  content: ['./app/**/*.{vue,js,ts}', './nuxt.config.ts'],
  theme: {
    fontFamily: {
      sans: ['"Source Sans Pro"', 'BlinkMacSystemFont', 'sans-serif'],
    },
    extend: {
      colors: {
        orange: {
          300: '#fdba74',
        },
        blue: {
          600: '#006eba',
          700: '#005a9e',
        },
      },
    },
  },
  plugins: [],
}
