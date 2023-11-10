import { hashParams } from "api/utils";

const testCases = {
  primitives: [
    {
      input: null,
      expected: 3938
    },
    {
      input: undefined,
      expected: 3938
    },
    {
      input: 123,
      expected: 48690
    },
    {
      input: "123",
      expected: 32909138
    },
    {
      input: true,
      expected: 3569038
    }
  ],
  objects: [
    {
      input: [123],
      expected: 85549894
    },
    {
      input: { c: "1", a: [1, 2, 3] },
      expected: -1632154681
    },
    {
      input: {},
      expected: 3938
    },
    {
      input: [],
      expected: 2914
    }
  ]
};

const stabilityTestCases = {
  "reordered properties names": [
    { b: 1, c: 2, a: [3, 4, 1] },
    { c: 2, b: 1, a: [3, 4, 1] }
  ],
  "property value reordered array": [
    { b: 1, c: 2, a: [3, 4, 1] },
    { b: 1, c: 2, a: [1, 4, 3] }
  ],
  "reordered arrays": [
    [1, 2, 3],
    [3, 2, 1]
  ]
};

describe("hashParams works on different data", () => {
  Object.entries(testCases).forEach(([testName, tests]) => {
    test(testName, () => {
      tests.forEach(({ input, expected }) => {
        expect(hashParams(input)).toEqual(expected);
      });
    });
  });
});

describe("hashParams util does not mutate originals", () => {
  Object.entries(stabilityTestCases).forEach(([testName, [input1, input2]]) => {
    test(testName, () => {
      const compareBeforeAndAfter = (input) => {
        const savedJson = JSON.stringify(input);
        hashParams(input);
        expect(savedJson).toEqual(JSON.stringify(input));
      };

      compareBeforeAndAfter(input1);
      compareBeforeAndAfter(input2);
    });
  });
});

describe("hashParams util returns the same result for differently sorted inputs", () => {
  Object.entries(stabilityTestCases).forEach(([testName, [input1, input2]]) => {
    test(testName, () => {
      expect(hashParams(input1)).toEqual(hashParams(input2));
    });
  });
});
