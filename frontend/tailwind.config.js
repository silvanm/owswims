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
      },
    },
  },
  variants: {},
  plugins: [require('@tailwindcss/custom-forms')],
}
