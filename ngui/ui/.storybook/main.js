module.exports = {
  core: {
    builder: "webpack5"
  },
  reactOptions: {
    strictMode: true
  },
  stories: ["../src/stories/**/*.stories.js"],
  addons: [
    "@storybook/addon-controls",
    "@storybook/addon-actions",
    "@storybook/addon-links",
    "@storybook/preset-create-react-app",
    "@storybook/addon-backgrounds"
  ]
};
