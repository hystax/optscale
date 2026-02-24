export const THEME_RESOLVER_CONFIG = {
  // List of supported file extensions and index files to resolve for theme overrides
  extensions: [
    "",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".mjs",
    ".cjs",
    ".css",
    ".scss",
    ".sass",
    ".less",
    ".json",
    "/index.tsx",
    "/index.ts",
    "/index.js",
    "/index.jsx",
    "/index.mjs",
    "/index.cjs",
    "/index.css",
  ],
  themesDir: "themes", // Directory where themes are stored
  srcDir: "src", // Source directory for resolving relative paths
};
