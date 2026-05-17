import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig(({ command }) => ({
  plugins: [react()],

  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src/app"),
    },
  },

  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:5000",
        changeOrigin: true,
      },
      "/gdl-turismo": {
        target: "http://localhost:5000",
        changeOrigin: true,
      },
      "/static": {
        target: "http://localhost:5000",
        changeOrigin: true,
      },
    },
  },

  build: {
    outDir: "../apps/frontend_web/static/react",
    emptyOutDir: true,
  },

  base: command === "build" ? "/static/react/" : "/",
}));