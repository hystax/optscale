import { splitInvites } from "utils/strings";

const testCases = {
  "single value": {
    expected: ["a@m.com"],
    inputs: ["a@m.com", "    a@m.com", "a@m.com    ", "    a@m.com      "]
  },
  "with whitespace sepator": {
    expected: ["a@m.com", "b@m.com"],
    inputs: ["a@m.com b@m.com", "    a@m.com    b@m.com     "]
  },
  "with comma separator": {
    expected: ["a@m.com", "b@m.com"],
    inputs: [
      "a@m.com, b@m.com",
      "a@m.com  , b@m.com",
      "a@m.com  , b@m.com",
      "    a@m.com, b@m.com    ",
      ",a@m.com     ,b@m.com,",
      ",   a@m.com     ,b@m.com   ,    "
    ]
  },
  "with semicolon separator": {
    expected: ["a@m.com", "b@m.com"],
    inputs: [
      "a@m.com; b@m.com",
      "a@m.com  ; b@m.com",
      "a@m.com  ; b@m.com",
      "    a@m.com; b@m.com    ",
      ";a@m.com     ;b@m.com;",
      ";   a@m.com     ;b@m.com   ;    "
    ]
  },
  "with mixed sepatators": {
    expected: ["a@m.com", "b@m.com", "c@m.com", "d@m.com", "e@m.com", "f@m.com", "g@m.com", "h@m.com", "i@m.com", "j@m.com"],
    inputs: ["     a@m.com,b@m.com;c@m.com d@m.com, e@m.com; f@m.com  g@m.com   ,    h@m.com    ;    i@m.com       j@m.com    "]
  }
};

describe("splitInvites util testing", () => {
  Object.entries(testCases).forEach(([testName, { expected, inputs }]) => {
    test(testName, () => {
      inputs.forEach((input) => {
        expect(splitInvites(input)).toEqual(expected);
      });
    });
  });
});
