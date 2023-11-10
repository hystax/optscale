import { areSearchParamsEqual } from "api/utils";

describe("Testing areSearchParamsEqual utility function", () => {
  it("Should return correct result if values are the same", () => {
    const params1 = {
      foo: "1"
    };
    const params2 = {
      foo: "1"
    };

    expect(areSearchParamsEqual(params1, params2)).toEqual(true);
  });
  it("Should return correct result if values are the same but in different formats - string and an array", () => {
    const params1 = {
      foo: "1"
    };
    const params2 = {
      foo: ["1"]
    };

    expect(areSearchParamsEqual(params1, params2)).toEqual(true);
  });
  it("Should return correct result if some values are explicitly undefined", () => {
    const params1 = {
      foo: undefined
    };
    const params2 = {
      foo: ["1"]
    };

    expect(areSearchParamsEqual(params1, params2)).toEqual(false);
  });
  it("Should return correct result if some values are explicitly undefined", () => {
    const params1 = {
      bar: undefined,
      foo: "1"
    };
    const params2 = {
      foo: ["1"]
    };

    expect(areSearchParamsEqual(params1, params2)).toEqual(true);
  });
  it("Should return correct result if values are the same arrays", () => {
    const params1 = {
      foo: ["1", "2"]
    };
    const params2 = {
      foo: ["1", "2"]
    };

    expect(areSearchParamsEqual(params1, params2)).toEqual(true);
  });
  it("Should return correct result if values are different", () => {
    const params1 = {
      foo: "1"
    };
    const params2 = {
      foo: "2"
    };

    expect(areSearchParamsEqual(params1, params2)).toEqual(false);
  });
  it("Should return correct result if values are the same arrays but with different values order", () => {
    const params1 = {
      foo: ["1", "2", "3"]
    };
    const params2 = {
      foo: ["2", "1", "3"]
    };

    expect(areSearchParamsEqual(params1, params2)).toEqual(true);
  });
  it("Should return correct result if values are arrays with different length with different values", () => {
    const params1 = {
      foo: ["1", "2", "3"]
    };
    const params2 = {
      foo: ["1", "2", "3", "4"]
    };

    expect(areSearchParamsEqual(params1, params2)).toEqual(false);
  });
  it("Should return correct result if values are arrays with the same length and with different values", () => {
    const params1 = {
      foo: ["1", "2", "3"]
    };
    const params2 = {
      foo: ["4", "5", "6"]
    };

    expect(areSearchParamsEqual(params1, params2)).toEqual(false);
  });
  it("Should return correct result if parameter doesn't exist in new search params", () => {
    const params1 = {
      foo: ["1", "2", "3"]
    };
    const params2 = {
      bar: "1"
    };

    expect(areSearchParamsEqual(params1, params2)).toEqual(false);
  });
  it("Should return correct result if parameters have different shapes", () => {
    const params1 = {
      foo: ["1", "2", "3"],
      bar: "1",
      foofoo: ["2", "3"]
    };
    const params2 = {
      bar: "1",
      baz: "hello world",
      hi: "hello",
      foo: "1"
    };

    expect(areSearchParamsEqual(params1, params2)).toEqual(false);
  });
});
