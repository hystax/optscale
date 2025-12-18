import react from "@vitejs/plugin-react-swc";
import { defineConfig, loadEnv } from "vite";
import tsconfigPaths from "vite-tsconfig-paths";

const parseViteHost = (value?: string): string | boolean => {
  const trimmed = value?.trim();
  if (!trimmed) return false;

  const lower = trimmed.toLowerCase();
  if (lower === "true") return true;
  if (lower === "false") return false;

  return trimmed;
};

const parseAllowedHosts = (value?: string): true | string[] | undefined => {
  const trimmed = value?.trim();
  if (!trimmed) return undefined;

  const lower = trimmed.toLowerCase();
  if (lower === "true") return true;
  if (lower === "false") return undefined;

  return trimmed.split(",").map((host) => host.trim());
};

const getBuildDir = (dir?: string): string => {
  if (!dir) {
    return "build";
  }
  const normalized = dir.trim();
  // Prevent path traversal and absolute paths
  if (normalized.includes("..") || normalized.startsWith("/")) {
    throw new Error(`Invalid VITE_BUILD_DIR: path traversal and absolute paths are not allowed`);
  }
  return dir;
};

export default defineConfig(({ mode }) => {
  // https://vitejs.dev/guide/api-javascript.html#loadenv
  const env = loadEnv(mode, process.cwd());

  const { VITE_BUILD_DIR, VITE_PORT, VITE_PROXY, VITE_PREVIEW_PORT, VITE_HOST, VITE_ALLOWED_HOSTS } = env;

  return {
    build: {
      outDir: getBuildDir(VITE_BUILD_DIR),
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
      host: parseViteHost(VITE_HOST),
      allowedHosts: parseAllowedHosts(VITE_ALLOWED_HOSTS),
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
