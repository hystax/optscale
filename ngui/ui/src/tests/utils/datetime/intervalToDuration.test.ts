import { intervalToDuration, INTERVAL_DURATION_VALUE_TYPES } from "utils/datetime";

describe("datetime utils: intervalToDuration", () => {
  it("returns zeros for the same dates", () => {
    const date = new Date();

    const result = intervalToDuration({ start: date, end: date });

    expect(result).toEqual({
      [INTERVAL_DURATION_VALUE_TYPES.WEEKS]: 0,
      [INTERVAL_DURATION_VALUE_TYPES.DAYS]: 0,
      [INTERVAL_DURATION_VALUE_TYPES.HOURS]: 0,
      [INTERVAL_DURATION_VALUE_TYPES.MINUTES]: 0,
      [INTERVAL_DURATION_VALUE_TYPES.SECONDS]: 0,
      [INTERVAL_DURATION_VALUE_TYPES.MILLISECONDS]: 0
    });
  });
  describe("returns correct duration for arbitrary dates", () => {
    it("case 1", () => {
      const start = new Date(2020, 2, 1, 12, 0, 0, 0);
      const end = new Date(2021, 3, 2, 13, 1, 1, 1);
      const result = intervalToDuration({ start, end });

      expect(result).toEqual({
        [INTERVAL_DURATION_VALUE_TYPES.WEEKS]: 56,
        [INTERVAL_DURATION_VALUE_TYPES.DAYS]: 5,
        [INTERVAL_DURATION_VALUE_TYPES.HOURS]: 1,
        [INTERVAL_DURATION_VALUE_TYPES.MINUTES]: 1,
        [INTERVAL_DURATION_VALUE_TYPES.SECONDS]: 1,
        [INTERVAL_DURATION_VALUE_TYPES.MILLISECONDS]: 1
      });
    });
    it("case 2", () => {
      const start = new Date(2021, 0, 1, 12, 30, 0, 0);
      const end = new Date(2021, 0, 23, 13, 31, 59, 50);

      const result = intervalToDuration({ start, end });

      expect(result).toEqual({
        [INTERVAL_DURATION_VALUE_TYPES.WEEKS]: 3,
        [INTERVAL_DURATION_VALUE_TYPES.DAYS]: 1,
        [INTERVAL_DURATION_VALUE_TYPES.HOURS]: 1,
        [INTERVAL_DURATION_VALUE_TYPES.MINUTES]: 1,
        [INTERVAL_DURATION_VALUE_TYPES.SECONDS]: 59,
        [INTERVAL_DURATION_VALUE_TYPES.MILLISECONDS]: 50
      });
    });
    it("case 3", () => {
      const start = new Date(2021, 0, 1, 14, 30, 10, 10);
      const end = new Date(2021, 0, 23, 13, 31, 5, 0);

      const result = intervalToDuration({ start, end });

      expect(result).toEqual({
        [INTERVAL_DURATION_VALUE_TYPES.WEEKS]: 3,
        [INTERVAL_DURATION_VALUE_TYPES.DAYS]: 0,
        [INTERVAL_DURATION_VALUE_TYPES.HOURS]: 23,
        [INTERVAL_DURATION_VALUE_TYPES.MINUTES]: 0,
        [INTERVAL_DURATION_VALUE_TYPES.SECONDS]: 54,
        [INTERVAL_DURATION_VALUE_TYPES.MILLISECONDS]: 990
      });
    });
    it("case 4", () => {
      const start = new Date(2021, 0, 1, 12, 30, 0, 0);
      const end = new Date(2021, 0, 23, 13, 31, 59, 50);

      const result = intervalToDuration({ start: end, end: start });

      expect(result).toEqual({
        [INTERVAL_DURATION_VALUE_TYPES.WEEKS]: 3,
        [INTERVAL_DURATION_VALUE_TYPES.DAYS]: 1,
        [INTERVAL_DURATION_VALUE_TYPES.HOURS]: 1,
        [INTERVAL_DURATION_VALUE_TYPES.MINUTES]: 1,
        [INTERVAL_DURATION_VALUE_TYPES.SECONDS]: 59,
        [INTERVAL_DURATION_VALUE_TYPES.MILLISECONDS]: 50
      });
    });
  });

  // Took samples from https://github.com/date-fns/date-fns/blob/master/src/intervalToDuration/test.ts#L52
  describe("edge cases", () => {
    it("returns correct duration for dates in the end of Feb", () => {
      expect(
        intervalToDuration({
          start: new Date(2012, 1, 28, 9, 0, 0),
          end: new Date(2012, 1, 29, 10, 0, 0)
        })
      ).toEqual({
        [INTERVAL_DURATION_VALUE_TYPES.WEEKS]: 0,
        [INTERVAL_DURATION_VALUE_TYPES.DAYS]: 1,
        [INTERVAL_DURATION_VALUE_TYPES.HOURS]: 1,
        [INTERVAL_DURATION_VALUE_TYPES.MINUTES]: 0,
        [INTERVAL_DURATION_VALUE_TYPES.SECONDS]: 0,
        [INTERVAL_DURATION_VALUE_TYPES.MILLISECONDS]: 0
      });

      expect(
        intervalToDuration({
          start: new Date(2012, 1, 29, 9, 0, 0),
          end: new Date(2012, 1, 29, 10, 0, 0)
        })
      ).toEqual({
        [INTERVAL_DURATION_VALUE_TYPES.WEEKS]: 0,
        [INTERVAL_DURATION_VALUE_TYPES.DAYS]: 0,
        [INTERVAL_DURATION_VALUE_TYPES.HOURS]: 1,
        [INTERVAL_DURATION_VALUE_TYPES.MINUTES]: 0,
        [INTERVAL_DURATION_VALUE_TYPES.SECONDS]: 0,
        [INTERVAL_DURATION_VALUE_TYPES.MILLISECONDS]: 0
      });

      expect(
        intervalToDuration({
          start: new Date(2012, 1, 28, 9, 0, 0),
          end: new Date(2012, 1, 28, 10, 0, 0)
        })
      ).toEqual({
        [INTERVAL_DURATION_VALUE_TYPES.WEEKS]: 0,
        [INTERVAL_DURATION_VALUE_TYPES.DAYS]: 0,
        [INTERVAL_DURATION_VALUE_TYPES.HOURS]: 1,
        [INTERVAL_DURATION_VALUE_TYPES.MINUTES]: 0,
        [INTERVAL_DURATION_VALUE_TYPES.SECONDS]: 0,
        [INTERVAL_DURATION_VALUE_TYPES.MILLISECONDS]: 0
      });

      expect(
        intervalToDuration({
          start: new Date(2021, 1, 28, 7, 23, 7),
          end: new Date(2021, 1, 28, 7, 38, 18)
        })
      ).toEqual({
        [INTERVAL_DURATION_VALUE_TYPES.WEEKS]: 0,
        [INTERVAL_DURATION_VALUE_TYPES.DAYS]: 0,
        [INTERVAL_DURATION_VALUE_TYPES.HOURS]: 0,
        [INTERVAL_DURATION_VALUE_TYPES.MINUTES]: 15,
        [INTERVAL_DURATION_VALUE_TYPES.SECONDS]: 11,
        [INTERVAL_DURATION_VALUE_TYPES.MILLISECONDS]: 0
      });
    });
  });
});
