import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import type { Plugin } from "vite";
import { THEME_RESOLVER_CONFIG } from "./config";

/**
 * Vite plugin to resolve theme-specific files based on the active theme.
 * The theme name must match the folder name in the themes' directory.
 *
 * @param theme - The active theme name (must match folder name in themes directory).
 * @returns Vite plugin instance.
 */
export function ThemeResolver(theme: string): Plugin {
  const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../");
  const themeBase = path.resolve(projectRoot, `${THEME_RESOLVER_CONFIG.themesDir}/${theme}`);

  /**
   * Returns file stats if the file exists, otherwise returns null.
   *
   * @param filePath - Absolute path to the file.
   * @returns fs.Stats object if file exists, otherwise null.
   */
  const getFileStatIfExists = (filePath: string) => {
    try {
      return fs.statSync(filePath);
    } catch {
      return null;
    }
  };

  /**
   * Resolves a file path by checking for valid extensions and index files.
   *
   * @param filePath - Base file path to resolve.
   * @returns Resolved file path with valid extension, or null if not found.
   */
  const resolveWithExtensions = (filePath: string): string | null =>
    THEME_RESOLVER_CONFIG.extensions
      .map((ext) => (ext.startsWith("/") ? path.join(filePath, ext) : `${filePath}${ext}`))
      .find((filePath) => getFileStatIfExists(filePath)?.isFile()) || null;

  /**
   * Redirects an absolute file path to its theme-specific equivalent if available.
   *
   * @param absolutePath - Absolute path to the original file.
   * @returns Theme-specific file path if found, otherwise null.
   */
  const redirectToThemePath = (absolutePath: string): string | null => {
    const relativePath = path.relative(projectRoot, absolutePath).replace(/\\/g, "/");
    if (relativePath.startsWith(`${THEME_RESOLVER_CONFIG.themesDir}/${theme}/`)) return null;
    return resolveWithExtensions(
      path.join(themeBase, relativePath.replace(new RegExp(`^${THEME_RESOLVER_CONFIG.srcDir}/`), ""))
    );
  };

  return {
    name: "vite-theme-resolver",
    enforce: "pre",

    /**
     * Vite hook to resolve module IDs, redirecting to theme-specific files if available.
     */
    async resolveId(source, importer, options) {
      if (!importer) return null;

      const resolved = await this.resolve(source, importer, { skipSelf: true, ...options });
      if (!resolved?.id?.startsWith("/")) return null;

      return redirectToThemePath(resolved.id);
    },
  };
}
