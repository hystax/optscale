/* eslint-disable */
const fs = require("fs-extra");
const { glob } = require("glob");
const TRANSLATION_PATH = "src/translations/**/*.json";
(async function TranslationSorting() {
  const res = await glob(TRANSLATION_PATH, function (readFolderError, files) {
    if (readFolderError) {
      console.log("cannot read the folder, something goes wrong with glob: ".concat(readFolderError));
    }
    files.forEach(function (file) {
      fs.readFile(file, "utf8", function (readFileError, contents) {
        if (readFileError) {
          console.log("cannot read the file: ".concat(readFileError));
        }
        var orderedJson = {};
        var parsefile = JSON.parse(contents);
        Object.keys(parsefile)
          .sort()
          .forEach(function (key) {
            orderedJson[key] = parsefile[key];
          });
        fs.writeFile(file, JSON.stringify(orderedJson));
      });
    });
  });

  res.forEach(function (file) {
    fs.readFile(file, "utf8", function (readFileError, contents) {
      if (readFileError) {
        console.log("cannot read the file: ".concat(readFileError));
      }
      var orderedJson = {};
      var parsefile = JSON.parse(contents);
      Object.keys(parsefile)
        .sort()
        .forEach(function (key) {
          orderedJson[key] = parsefile[key];
        });
      fs.writeFile(file, JSON.stringify(orderedJson));
    });
  });
})();
