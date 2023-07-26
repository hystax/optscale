import { sortObjectsAlphabetically } from "utils/arrays";

describe("Sort array of object alphabetically by provided key", () => {
  test("Should not mutate provided array", () => {
    const sourceArray = [{ name: "A" }, { name: "d" }, { name: "b" }, { name: "123" }];
    sortObjectsAlphabetically({ array: sourceArray, field: "name" });

    expect(sourceArray).toEqual([{ name: "A" }, { name: "d" }, { name: "b" }, { name: "123" }]);
  });
  test("Should return a new array", () => {
    const sourceArray = [{ name: "A" }, { name: "d" }, { name: "b" }, { name: "123" }];
    const sortedArray = sortObjectsAlphabetically({ array: sourceArray, field: "name" });

    expect(sourceArray === sortedArray).toBeFalsy();
  });
  test("Should be case insensitive", () => {
    const sourceArray = [
      { name: "a" },
      { name: "b" },
      { name: "c" },
      { name: "1984" },
      { name: "A" },
      { name: "B" },
      { name: "C" }
    ];
    const sortedArray = sortObjectsAlphabetically({ array: sourceArray, field: "name" });

    expect(sortedArray).toEqual([
      { name: "1984" },
      { name: "a" },
      { name: "A" },
      { name: "b" },
      { name: "B" },
      { name: "c" },
      { name: "C" }
    ]);
  });
  test("Should respect locale", () => {
    const sourceArray = [{ name: "c" }, { name: "č" }, { name: "é" }, { name: "A" }, { name: "b" }, { name: "Đ" }];
    const sortedArray = sortObjectsAlphabetically({ array: sourceArray, field: "name" });

    expect(sortedArray).toEqual([{ name: "A" }, { name: "b" }, { name: "c" }, { name: "č" }, { name: "Đ" }, { name: "é" }]);
  });
});
