import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        muted: "hsl(var(--muted))",
        panel: "hsl(var(--panel))",
        primary: "hsl(var(--primary))",
        accent: "hsl(var(--accent))",
        warning: "hsl(var(--warning))"
      },
      boxShadow: {
        soft: "0 1px 2px rgba(15, 23, 42, 0.08), 0 8px 28px rgba(15, 23, 42, 0.06)"
      }
    }
  },
  plugins: []
};

export default config;

