import { describe, expect, it } from "vitest";
import { CONNECTION_MODES, DEFAULT_FILE_PATTERN, FIELD_NAMES } from "./constants";
import {
  getFocusAccessKeyId,
  getFocusConfigParams,
  getFocusDefaultValues,
  getFocusUpdateConfigParams,
  isFocusAutoImport,
  isHttpsEndpoint,
  isKeyPairConsistent,
} from "./utils";

describe("isFocusAutoImport", () => {
  it.each([
    ["the bucket mode", CONNECTION_MODES.BUCKET, true],
    ["the manual upload mode", CONNECTION_MODES.MANUAL_UPLOAD, false],
    ["no mode", undefined, false],
  ])("is %s -> %s", (_, connectionMode, expected) => {
    expect(isFocusAutoImport({ [FIELD_NAMES.CONNECTION_MODE]: connectionMode })).toBe(expected);
  });
});

describe("isHttpsEndpoint", () => {
  it.each([
    ["", true],
    ["https://minio.example.com", true],
    ["HTTPS://storage.example.com:9000", true],
    ["http://minio.example.com", false],
    ["minio.example.com", false],
    ["https://", false],
    ["https://:9000", false],
    ["https:// minio.example.com", false],
  ])("%j -> %s", (value, expected) => {
    expect(isHttpsEndpoint(value)).toBe(expected);
  });
});

describe("isKeyPairConsistent", () => {
  it.each([
    ["", "", true],
    ["AKIA", "secret", true],
    ["AKIA", "", false],
    ["", "secret", false],
    [" ", "secret", false],
  ])("access key %j, secret %j -> %s", (accessKeyId, secretAccessKey, expected) => {
    expect(isKeyPairConsistent(accessKeyId, secretAccessKey)).toBe(expected);
  });
});

describe("getFocusConfigParams", () => {
  it("sends no bucket fields and no credentials in manual upload mode", () => {
    expect(
      getFocusConfigParams({
        [FIELD_NAMES.CONNECTION_MODE]: CONNECTION_MODES.MANUAL_UPLOAD,
        // Values left after switching back from the bucket mode
        [FIELD_NAMES.BUCKET_NAME]: "reports",
        [FIELD_NAMES.ACCESS_KEY_ID]: "AKIA",
        [FIELD_NAMES.SECRET_ACCESS_KEY]: "secret",
      })
    ).toEqual({});
  });

  it("sends only the bucket name when the optional bucket fields are empty", () => {
    expect(
      getFocusConfigParams({
        [FIELD_NAMES.CONNECTION_MODE]: CONNECTION_MODES.BUCKET,
        [FIELD_NAMES.BUCKET_NAME]: "reports",
        [FIELD_NAMES.BUCKET_PREFIX]: "",
        [FIELD_NAMES.S3_ENDPOINT]: "",
        [FIELD_NAMES.REGION_NAME]: "",
        [FIELD_NAMES.ACCESS_KEY_ID]: "",
        [FIELD_NAMES.SECRET_ACCESS_KEY]: "",
        [FIELD_NAMES.FILE_PATTERN]: "",
      })
    ).toEqual({ bucket_name: "reports" });
  });

  it("sends all filled bucket fields without surrounding whitespace", () => {
    expect(
      getFocusConfigParams({
        [FIELD_NAMES.CONNECTION_MODE]: CONNECTION_MODES.BUCKET,
        [FIELD_NAMES.BUCKET_NAME]: " reports ",
        [FIELD_NAMES.BUCKET_PREFIX]: "exports/focus/",
        [FIELD_NAMES.S3_ENDPOINT]: "https://minio.example.com",
        [FIELD_NAMES.REGION_NAME]: "eu-central-1",
        [FIELD_NAMES.FILE_PATTERN]: "\\.parquet$ ",
      })
    ).toEqual({
      bucket_name: "reports",
      bucket_prefix: "exports/focus/",
      s3_endpoint: "https://minio.example.com",
      region_name: "eu-central-1",
      file_pattern: "\\.parquet$",
    });
  });

  it("sends the access key pair as credentials", () => {
    expect(
      getFocusConfigParams({
        [FIELD_NAMES.CONNECTION_MODE]: CONNECTION_MODES.BUCKET,
        [FIELD_NAMES.BUCKET_NAME]: "reports",
        [FIELD_NAMES.ACCESS_KEY_ID]: "AKIAEXAMPLE",
        [FIELD_NAMES.SECRET_ACCESS_KEY]: "wJalrXUtnFEMI/K7MDENG",
      })
    ).toEqual({
      bucket_name: "reports",
      credentials: {
        access_key_id: "AKIAEXAMPLE",
        secret_access_key: "wJalrXUtnFEMI/K7MDENG",
      },
    });
  });

  it("sends no credentials for anonymous access when both keys are empty", () => {
    expect(
      getFocusConfigParams({
        [FIELD_NAMES.CONNECTION_MODE]: CONNECTION_MODES.BUCKET,
        [FIELD_NAMES.BUCKET_NAME]: "public-reports",
        [FIELD_NAMES.ACCESS_KEY_ID]: " ",
        [FIELD_NAMES.SECRET_ACCESS_KEY]: "",
      })
    ).toEqual({ bucket_name: "public-reports" });
  });
});

describe("getFocusDefaultValues", () => {
  it("prefills the bucket mode and the stored bucket fields, with empty keys", () => {
    expect(
      getFocusDefaultValues({
        bucket_name: "reports",
        bucket_prefix: "exports/focus/",
        s3_endpoint: "https://minio.example.com",
        region_name: "eu-central-1",
        file_pattern: "\\.parquet$",
        mapping: { resource_id: { columns: ["ResourceId"] } },
      })
    ).toEqual({
      [FIELD_NAMES.CONNECTION_MODE]: CONNECTION_MODES.BUCKET,
      [FIELD_NAMES.BUCKET_NAME]: "reports",
      [FIELD_NAMES.BUCKET_PREFIX]: "exports/focus/",
      [FIELD_NAMES.S3_ENDPOINT]: "https://minio.example.com",
      [FIELD_NAMES.REGION_NAME]: "eu-central-1",
      [FIELD_NAMES.ACCESS_KEY_ID]: "",
      [FIELD_NAMES.SECRET_ACCESS_KEY]: "",
      [FIELD_NAMES.FILE_PATTERN]: "\\.parquet$",
    });
  });

  it("prefills the stored access key ID and leaves the secret access key empty", () => {
    expect(getFocusDefaultValues({ bucket_name: "reports", credentials: { access_key_id: "AKIAEXAMPLE" } })).toMatchObject({
      [FIELD_NAMES.ACCESS_KEY_ID]: "AKIAEXAMPLE",
      [FIELD_NAMES.SECRET_ACCESS_KEY]: "",
    });
  });

  it("prefills empty strings for the bucket fields the source does not have", () => {
    expect(getFocusDefaultValues({ bucket_name: "reports", bucket_prefix: null })).toEqual({
      [FIELD_NAMES.CONNECTION_MODE]: CONNECTION_MODES.BUCKET,
      [FIELD_NAMES.BUCKET_NAME]: "reports",
      [FIELD_NAMES.BUCKET_PREFIX]: "",
      [FIELD_NAMES.S3_ENDPOINT]: "",
      [FIELD_NAMES.REGION_NAME]: "",
      [FIELD_NAMES.ACCESS_KEY_ID]: "",
      [FIELD_NAMES.SECRET_ACCESS_KEY]: "",
      [FIELD_NAMES.FILE_PATTERN]: "",
    });
  });

  it.each([
    ["no config", undefined],
    ["an empty config", {}],
    ["a config with a mapping only", { mapping: { cost: { columns: ["BilledCost"] } } }],
    ["a manual upload config saved by the Update credentials form", { file_pattern: DEFAULT_FILE_PATTERN }],
  ])("prefills the manual upload mode for %s", (_, config) => {
    expect(getFocusDefaultValues(config)).toEqual({
      [FIELD_NAMES.CONNECTION_MODE]: CONNECTION_MODES.MANUAL_UPLOAD,
      [FIELD_NAMES.BUCKET_NAME]: "",
      [FIELD_NAMES.BUCKET_PREFIX]: "",
      [FIELD_NAMES.S3_ENDPOINT]: "",
      [FIELD_NAMES.REGION_NAME]: "",
      [FIELD_NAMES.ACCESS_KEY_ID]: "",
      [FIELD_NAMES.SECRET_ACCESS_KEY]: "",
      [FIELD_NAMES.FILE_PATTERN]: "",
    });
  });
});

describe("getFocusAccessKeyId", () => {
  it.each([
    ["no config", undefined],
    ["no credentials", { bucket_name: "reports" }],
    ["null credentials", { bucket_name: "reports", credentials: null }],
    ["empty credentials", { bucket_name: "reports", credentials: {} }],
    ["an empty access key ID", { bucket_name: "reports", credentials: { access_key_id: "" } }],
  ])("is undefined for anonymous access with %s", (_, config) => {
    expect(getFocusAccessKeyId(config)).toBeUndefined();
  });

  it("returns the stored access key ID", () => {
    expect(getFocusAccessKeyId({ credentials: { access_key_id: "AKIAEXAMPLE" } })).toBe("AKIAEXAMPLE");
  });
});

describe("getFocusUpdateConfigParams", () => {
  it("sends the bucket config in bucket mode", () => {
    expect(
      getFocusUpdateConfigParams({
        [FIELD_NAMES.CONNECTION_MODE]: CONNECTION_MODES.BUCKET,
        [FIELD_NAMES.BUCKET_NAME]: "reports",
        [FIELD_NAMES.BUCKET_PREFIX]: "exports/",
        [FIELD_NAMES.ACCESS_KEY_ID]: "",
        [FIELD_NAMES.SECRET_ACCESS_KEY]: "",
      })
    ).toEqual({ bucket_name: "reports", bucket_prefix: "exports/" });
  });

  // The API ignores an empty config on update, so the bucket would be kept
  it("sends a non-empty config without a bucket and credentials in manual upload mode", () => {
    expect(
      getFocusUpdateConfigParams({
        [FIELD_NAMES.CONNECTION_MODE]: CONNECTION_MODES.MANUAL_UPLOAD,
        // Prefilled values of the source that is being switched from a bucket
        [FIELD_NAMES.BUCKET_NAME]: "reports",
        [FIELD_NAMES.FILE_PATTERN]: "focus_(.*",
        [FIELD_NAMES.ACCESS_KEY_ID]: "AKIA",
        [FIELD_NAMES.SECRET_ACCESS_KEY]: "secret",
      })
    ).toEqual({ file_pattern: DEFAULT_FILE_PATTERN });
  });
});
