export const FIELD_NAMES = Object.freeze({
  NAME: "name",
  EXPORTED_DAYS: "exportedDays",
  STORAGE_TYPE: "storageType",
  AWS_STORAGE: Object.freeze({
    AWS_ACCESS_KEY_ID_FIELD_NAME: "awsAccessKeyId",
    AWS_SECRET_ACCESS_KEY_FIELD_NAME: "awsSecretAccessKey",
    BUCKET_NAME_FIELD_NAME: "bucketName",
    S3_PATH_FIELD_NAME: "s3Prefix"
  }),
  AZURE_STORAGE: Object.freeze({
    CONNECTION_STRING_FIELD_NAME: "connectionString",
    CONTAINER_FIELD_NAME: "container"
  })
});
