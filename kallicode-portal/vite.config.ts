import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// El portal habla con la API local en dev vía proxy (evita CORS en desarrollo).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: { "/api": "http://localhost:8000" },
  },
});
