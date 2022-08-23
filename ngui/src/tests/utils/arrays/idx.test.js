import { idx } from "utils/objects";

const KEY = "key";

describe("idx util testing", () => {
  describe("Searching for falsy values", () => {
    const cases = [
      {
        value: 0,
        expected: 0
      },
      {
        value: false,
        expected: false
      },
      {
        value: null,
        expected: null
      },
      {
        value: undefined,
        expected: undefined
      },
      {
        value: NaN,
        expected: NaN
      }
    ];

    cases.forEach(({ value, expected }) => {
      test(`Should return ${expected}`, () => {
        const object = {
          [KEY]: value
        };
        const result = idx([KEY], object);
        expect(result).toEqual(expected);
      });
    });
  });
  describe("Target value is empty object", () => {
    test("Should return empty object", () => {
      const object = {
        [KEY]: {}
      };
      const result = idx([KEY], object);
      expect(result).toEqual({});
    });
  });
  describe("Target value is absent", () => {
    test("Should return undefined", () => {
      const object = {};
      const result = idx([KEY], object);
      expect(result).toEqual(undefined);
    });
  });
  describe("With defaultValue", () => {
    const defaultValue = "default value";

    test("Should return default value", () => {
      const object = {
        level1: {}
      };
      const result = idx(["level1", "level2"], object, defaultValue);
      expect(result).toEqual(defaultValue);
    });
    test("Should ignore default value", () => {
      const actualValue = false;
      const object = {
        level1: { level2: actualValue }
      };
      const result = idx(["level1", "level2"], object, defaultValue);
      expect(result).toEqual(actualValue);
    });
  });
  describe("Deep search", () => {
    test("Should find without crashing, returns 0", () => {
      const object = {
        level1: { level2: { level3: 0 } }
      };
      const result = idx(["level1", "level2", "level3"], object);
      expect(result).toEqual(0);
    });
  });
});
