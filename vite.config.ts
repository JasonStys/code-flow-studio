/** Offline renderer build; all editor workers are local. Symbols: docs/code-index.md. */
import {defineConfig} from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({root: "ui", plugins: [react()], build: {outDir: "../dist/ui", emptyOutDir: true}, server: {proxy: {"/api": "http://127.0.0.1:8012", "/health": "http://127.0.0.1:8012"}}});

