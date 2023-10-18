import { promises as fs } from "fs";
import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv } from "vite";
import tsconfigPaths from "vite-tsconfig-paths";

export default defineConfig(async ({ mode }) => {
  // https://vitejs.dev/guide/api-javascript.html#loadenv
  const env = loadEnv(mode, process.cwd());

  const { VITE_PORT, VITE_PROXY, VITE_PREVIEW_PORT } = env;

  return {
    entry: "index.js",
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
    plugins: [
      react(),
      /**
       * Resolve imports according to path settings in tsconfig
       */
      tsconfigPaths()
    ],
    resolve: {
      // https://github.com/vitest-dev/vitest/issues/2742#issuecomment-1406223702
      mainFields: ["module", "jsnext:main", "jsnext"]
    },
    test: {
      server: {
        deps: {
          inline: ["clsx", "@analytics/type-utils"]
        }
      },
      environment: "jsdom",
      globals: true
    },
    // TODO: Remove the "jsx" loader support as soon as we fully switch to .jsx/.tsx
    esbuild: {
      loader: "jsx",
      include: /src\/.*\.jsx?$/,
      exclude: []
    },
    optimizeDeps: {
      esbuildOptions: {
        plugins: [
          /**
           * TODO: Remove the "load-js-files-as-jsx" plugin as soon as we fully switch to .jsx/.tsx
           * https://github.com/vitejs/vite/discussions/3448
           */
          {
            name: "load-js-files-as-jsx",
            setup(build) {
              build.onLoad({ filter: /src\/.*\.js$/ }, async (args) => ({
                loader: "jsx",
                contents: await fs.readFile(args.path, "utf8")
              }));
            }
          }
        ]
      }
    }
  };
});
