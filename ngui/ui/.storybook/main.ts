import type { StorybookConfig } from "@storybook/react-vite";

const config: StorybookConfig = {
  framework: "@storybook/react-vite",
  stories: ["../src/stories/**/*.stories.tsx"],
  addons: ["@storybook/addon-controls", "@storybook/addon-actions", "@storybook/addon-links", "@storybook/addon-backgrounds"]
};

export default config;
