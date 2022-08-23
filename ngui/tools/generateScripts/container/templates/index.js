const containerTemplate = require("./containerTemplate");
const indexTemplate = require("./indexTemplate");

module.exports = (componentName) => ({
  index: {
    fileName: "index.js",
    template: indexTemplate(componentName)
  },
  container: {
    fileName: `${componentName}.js`,
    template: containerTemplate(componentName)
  }
});
