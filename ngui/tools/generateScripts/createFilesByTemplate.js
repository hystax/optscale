const { syncCreateFolderIfNotExists, syncWriteFile } = require("../fsUtils");

module.exports = (basePath, templates) => {
  const name = process.argv[2];

  if (name) {
    const fullPath = `${process.cwd()}/${basePath}/${name}`;

    syncCreateFolderIfNotExists(fullPath);

    Object.values(templates(name)).forEach(({ fileName, template }) => {
      syncWriteFile(fullPath, fileName, template);
    });
  }
};
