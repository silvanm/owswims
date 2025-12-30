module.exports = {
  future: {
    // removeDeprecatedGapUtilities: true,
    // purgeLayersByDefault: true,
  },
  purge: [],
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
  variants: {},
  plugins: [require('@tailwindcss/custom-forms')],
}
