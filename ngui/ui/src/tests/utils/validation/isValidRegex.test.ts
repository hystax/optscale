import { describe, expect, it } from "vitest";
import { isValidRegex } from "utils/validation";

describe("isValidRegex", () => {
  it.each([
    ["", true],
    ["\\.(csv|csv\\.gz|gz|zip|parquet)$", true],
    ["(?i)focus_.*\\.csv$", true],
    ["(?i)^microsoft\\.compute/disks$", true],
    ["^Run(?i)instances", true],
    ["(?i:run)instances", true],
    ["(?P<operation>Run)Instances", true],
    ["\\\\1", true],
    ["(?=Run)Instances", false],
    ["(?<!Stop)Instances", false],
    ["(\\w)\\1", false],
    ["focus_(.*\\.csv$", false],
    ["(?i)(disk", false],
    ["[a-", false],
  ])("%j -> %s", (value, expected) => {
    expect(isValidRegex(value)).toBe(expected);
  });
});
