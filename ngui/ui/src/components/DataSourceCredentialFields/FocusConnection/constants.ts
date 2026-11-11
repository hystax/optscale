export const FIELD_NAMES = Object.freeze({
  CONNECTION_MODE: "focusConnectionMode",
  BUCKET_NAME: "focusBucketName",
  BUCKET_PREFIX: "focusBucketPrefix",
  S3_ENDPOINT: "focusS3Endpoint",
  REGION_NAME: "focusRegionName",
  ACCESS_KEY_ID: "focusAccessKeyId",
  SECRET_ACCESS_KEY: "focusSecretAccessKey",
  FILE_PATTERN: "focusFilePattern",
});

export const CONNECTION_MODES = Object.freeze({
  MANUAL_UPLOAD: "manualUpload",
  BUCKET: "bucket",
});

// Used by the server when file_pattern is empty (matched case-insensitively)
export const DEFAULT_FILE_PATTERN = "\\.(csv|csv\\.gz|gz|zip|parquet)$";
