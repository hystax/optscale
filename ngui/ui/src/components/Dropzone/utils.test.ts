import { describe, expect, it } from "vitest";
import { isAcceptedFile } from "./utils";

const ACCEPTED_FILES = ["text/csv", ".csv", "", ".parquet"];

describe("isAcceptedFile", () => {
  it.each([
    ["an accepted MIME type", { name: "report.csv", type: "text/csv" }, true],
    ["an empty MIME type when it is accepted", { name: "report.parquet", type: "" }, true],
    ["an accepted extension with an unknown MIME type", { name: "report.parquet", type: "application/x-parquet" }, true],
    ["an accepted extension in another case", { name: "REPORT.CSV", type: "application/vnd.ms-excel" }, true],
    ["neither an accepted MIME type nor an accepted extension", { name: "report.json", type: "application/json" }, false],
    ["an accepted extension that is not the end of the name", { name: "report.csv.json", type: "application/json" }, false],
  ])("%s -> %s", (_, file, expected) => {
    expect(isAcceptedFile(file, ACCEPTED_FILES)).toBe(expected);
  });

  it("checks only the MIME type when no extension is accepted", () => {
    expect(isAcceptedFile({ name: "key.json", type: "application/json" }, ["application/json"])).toBe(true);
    expect(isAcceptedFile({ name: "key.json", type: "text/plain" }, ["application/json"])).toBe(false);
  });
});
