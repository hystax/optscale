import { describe, expect, it } from "vitest";
import { isAcceptedFile } from "components/Dropzone/utils";
import { AWS_CNR, FOCUS } from "utils/constants";
import { getAcceptedFileTypes } from "./utils";

describe("getAcceptedFileTypes", () => {
  it("accepts CSV and archives but not Parquet for AWS", () => {
    const fileTypes = getAcceptedFileTypes(AWS_CNR);

    expect(fileTypes).toEqual(
      expect.arrayContaining(["text/csv", ".csv", "application/gzip", ".gz", "application/zip", ".zip"])
    );
    expect(fileTypes).not.toContain(".parquet");
    expect(fileTypes).not.toContain("application/vnd.apache.parquet");
  });

  it.each(["report.csv.gz", "report.gz", "report.zip"])(
    "accepts %s reported as application/octet-stream by its extension",
    (name) => {
      expect(isAcceptedFile({ name, type: "application/octet-stream" }, getAcceptedFileTypes(FOCUS))).toBe(true);
    }
  );

  it("also accepts Parquet for FOCUS", () => {
    expect(getAcceptedFileTypes(FOCUS)).toEqual(
      expect.arrayContaining([
        "text/csv",
        ".csv",
        "application/gzip",
        "application/zip",
        ".parquet",
        "application/vnd.apache.parquet",
      ])
    );
  });
});
