import react from "@vitejs/plugin-react-swc";
import { defineConfig, loadEnv } from "vite";
import tsconfigPaths from "vite-tsconfig-paths";

export default defineConfig(({ mode }) => {
  // https://vitejs.dev/guide/api-javascript.html#loadenv
  const env = loadEnv(mode, process.cwd());

  const { VITE_PORT, VITE_PROXY, VITE_PREVIEW_PORT } = env;

  return {
    build: {
      outDir: "build",
      rollupOptions: {
        external: [
          // Exclude redux-immutable-state-invariant in order to prevent error on build when only production dependencies are installed
          "redux-immutable-state-invariant"
        ]
      }
    },
    server: {
      open: true,
      port: Number(VITE_PORT) || 3000,
      proxy: {
        "/api": {
          target: VITE_PROXY,
          changeOrigin: true,
          secure: false,
          rewrite: (p) => p.replace(/^\/api/, "/")
        }
      }
    },
    preview: {
      open: true,
      port: Number(VITE_PREVIEW_PORT) || 4000,
      proxy: Object.fromEntries(
        ["/auth", "/jira_bus", "/report", "/restapi", "/slacker"].map((name) => [
          name,
          {
            target: VITE_PROXY,
            changeOrigin: true,
            secure: false
          }
        ])
      )
    },
    plugins: [react(), tsconfigPaths()],
    // TODO: Some of the tests are still failing
    test: {
      server: {
        deps: {
          inline: ["clsx", "@analytics/type-utils"]
        }
      },
      environment: "jsdom",
      globals: true
    }
  };
});
