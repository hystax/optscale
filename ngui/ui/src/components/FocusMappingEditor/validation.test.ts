import { describe, expect, it } from "vitest";
import { hasColumnName, hasTemplatePlaceholder } from "./validation";

describe("hasColumnName", () => {
  it.each([
    [[], false],
    [["  "], false],
    [["BilledCost"], true],
    [["EffectiveCost", "BilledCost"], true],
  ])("%j -> %s", (columns, expected) => {
    expect(hasColumnName(columns)).toBe(expected);
  });
});

describe("hasTemplatePlaceholder", () => {
  it.each([
    ["no placeholder", false],
    ["{}", false],
    ["{ServiceName}/{SkuId}", true],
    ["prefix-{ResourceId}", true],
  ])("%j -> %s", (template, expected) => {
    expect(hasTemplatePlaceholder(template)).toBe(expected);
  });
});
