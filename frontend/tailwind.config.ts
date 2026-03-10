import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#EEF2FF",
          100: "#E0EAFF",
          200: "#C7D5FF",
          300: "#A4BAFF",
          400: "#7B93FF",
          500: "#4F46E5",
          600: "#4338CA",
          700: "#3730A3",
          800: "#312E81",
          900: "#1E1B4B",
        },
      },
      boxShadow: {
        premium: "0 18px 60px rgba(15, 23, 42, 0.15)",
        "premium-hover": "0 24px 80px rgba(15, 23, 42, 0.18)",
      },
    },
  },
  plugins: [],
};

export default config;
