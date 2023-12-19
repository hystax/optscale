import react from "@vitejs/plugin-react-swc";
import { defineConfig, loadEnv } from "vite";
import tsconfigPaths from "vite-tsconfig-paths";

export default defineConfig(({ mode }) => {
  // https://vitejs.dev/guide/api-javascript.html#loadenv
  const env = loadEnv(mode, process.cwd());

  const { VITE_PROXY } = env;

  return {
    build: {
      outDir: "build"
    },
    /*
      Jira ui project is deployed under a nested path
      https://vitejs.dev/guide/build#public-base-path
    */
    base: "/jira_ui",
    server: {
      open: true,
      port: 3001,
      proxy: {
        "/jira_bus": {
          target: VITE_PROXY,
          changeOrigin: true,
          secure: false
        }
      }
    },
    plugins: [react(), tsconfigPaths()]
  };
});
