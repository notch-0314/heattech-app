module.exports = {
  content: [
    "./src/app/**/*.{js,ts,jsx,tsx}",
    "frontend/src/app/condition/page.tsx",
    "frontend/src/app/recommended/page.tsx",
    "./src/components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}