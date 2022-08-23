const fs = require("fs-extra");
const glob = require("glob");

const TRANSLATION_PATH = "src/translations/**/*.json";

(function TranslationSorting() {
  glob(TRANSLATION_PATH, (readFolderError, files) => {
    if (readFolderError) {
      console.log(`cannot read the folder, something goes wrong with glob: ${readFolderError}`);
    }
    files.forEach((file) => {
      fs.readFile(file, "utf8", (readFileError, contents) => {
        if (readFileError) {
          console.log(`cannot read the file: ${readFileError}`);
        }
        const orderedJson = {};
        const parsefile = JSON.parse(contents);
        Object.keys(parsefile)
          .sort()
          .forEach((key) => {
            orderedJson[key] = parsefile[key];
          });
        fs.writeFile(file, JSON.stringify(orderedJson));
      });
    });
  });
})();
