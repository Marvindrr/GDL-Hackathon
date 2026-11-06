import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

const apiProxyTarget =
  process.env.API_PROXY_TARGET ?? "http://localhost:5000";

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
        target: apiProxyTarget,
        changeOrigin: true,
      },
      "/gdl-turismo": {
        target: apiProxyTarget,
        changeOrigin: true,
      },
      "/static": {
        target: apiProxyTarget,
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