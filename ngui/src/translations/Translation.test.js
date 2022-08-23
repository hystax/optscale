import defaultJson from "translations/en-US/app.json";
import errors from "translations/en-US/errors.json";

test("en translation file sorted alphabetically", () => {
  const orderedJson = {};

  Object.keys(defaultJson)
    .sort()
    .forEach((key) => {
      orderedJson[key] = defaultJson[key];
    });
  expect(JSON.stringify(defaultJson)).toEqual(JSON.stringify(orderedJson));
});

test("errors translation file sorted alphabetically", () => {
  const orderedJson = {};

  Object.keys(errors)
    .sort()
    .forEach((key) => {
      orderedJson[key] = errors[key];
    });
  expect(JSON.stringify(errors)).toEqual(JSON.stringify(orderedJson));
});
