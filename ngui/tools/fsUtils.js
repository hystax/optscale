const fs = require("fs");

const syncWriteFile = (path, fileName, content) => {
  const filePath = `${path}/${fileName}`;

  try {
    fs.writeFileSync(filePath, content);
    console.log("Created file: ", filePath);
  } catch (err) {
    console.error(err);
  }
};

const syncCreateFolderIfNotExists = (directoryPath) => {
  const isFolderExists = fs.existsSync(directoryPath);
  if (!isFolderExists) {
    fs.mkdirSync(directoryPath);
  }
};

module.exports = {
  syncWriteFile,
  syncCreateFolderIfNotExists
};
