module.exports = (componentName) => `import ${componentName} from "./${componentName}";

export default ${componentName};
`;
