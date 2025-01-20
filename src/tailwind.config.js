/** @type {import('tailwindcss').Config} */

//const plugin = require('tailwindcss/plugin')

module.exports = {
  content: [
    "./ufo/**/*.{html,js}",
    "./static/**/*.{html,js}",
    //"./templates/**/*.{html,js}"
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('daisyui'),
  ],
  daisyui: {
    themes: true,
    base: true, // applies background color and foreground color for root element by default
    styled: true, // include daisyUI colors and design decisions for all components
    utils: true, // adds responsive and modifier utility classes
  }
}

