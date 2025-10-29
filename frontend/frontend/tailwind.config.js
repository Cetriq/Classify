/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'klassa-blue': '#0066CC',
        'klassa-green': '#00AA55',
        'klassa-yellow': '#FFBB00',
        'klassa-red': '#DD3333',
      },
    },
  },
  plugins: [],
}
