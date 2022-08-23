const componentTemplate = require("./componentTemplate");
const indexTemplate = require("./indexTemplate");
const stylesTemplate = require("./stylesTemplate");
const testTemplate = require("./testTemplate");

module.exports = (componentName) => ({
  index: {
    fileName: "index.js",
    template: indexTemplate(componentName)
  },
  component: {
    fileName: `${componentName}.js`,
    template: componentTemplate(componentName)
  },
  styles: {
    fileName: `${componentName}.styles.js`,
    template: stylesTemplate
  },
  test: {
    fileName: `${componentName}.test.js`,
    template: testTemplate(componentName)
  }
});
