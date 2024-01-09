/* eslint-disable @typescript-eslint/no-var-requires */
const fs = require("fs");
const { glob } = require("glob");

const TRANSLATION_PATH = "src/translations/**/*.json";

(async function sortTranslations() {
  const files = await glob(TRANSLATION_PATH);

  files.forEach((file) => {
    try {
      const content = fs.readFileSync(file, { encoding: "utf8" });
      const parsedContent = JSON.parse(content);

      const output = Object.keys(parsedContent)
        .sort()
        .reduce((result, key) => ({ ...result, [key]: parsedContent[key] }), {});

      fs.writeFileSync(file, JSON.stringify(output));
    } catch (error) {
      console.log(error);
    }
  });
})();
