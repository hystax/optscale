import { BI_EXPORT_STORAGE_TYPE } from "utils/biExport";
import { FIELD_NAMES } from "./constants";
import { FormValues } from "./types";

export const getDefaultValues = (biExport = {}): FormValues => {
  const { name, days, type, meta: { access_key_id: accessKeyId, bucket, s3_prefix: s3Prefix, container } = {} } = biExport;

  return {
    [FIELD_NAMES.NAME]: name ?? "",
    [FIELD_NAMES.EXPORTED_DAYS]: days ?? "",
    [FIELD_NAMES.STORAGE_TYPE]: type ?? BI_EXPORT_STORAGE_TYPE.AWS_RAW_EXPORT,
    [FIELD_NAMES.AWS_STORAGE.AWS_ACCESS_KEY_ID_FIELD_NAME]: "",
    [FIELD_NAMES.AWS_STORAGE.AWS_SECRET_ACCESS_KEY_FIELD_NAME]: "",
    [FIELD_NAMES.AWS_STORAGE.BUCKET_NAME_FIELD_NAME]: "",
    [FIELD_NAMES.AWS_STORAGE.S3_PATH_FIELD_NAME]: "",
    [FIELD_NAMES.AZURE_STORAGE.CONNECTION_STRING_FIELD_NAME]: "",
    [FIELD_NAMES.AZURE_STORAGE.CONTAINER_FIELD_NAME]: "",
    ...(type === BI_EXPORT_STORAGE_TYPE.AWS_RAW_EXPORT
      ? {
          [FIELD_NAMES.AWS_STORAGE.AWS_ACCESS_KEY_ID_FIELD_NAME]: accessKeyId,
          [FIELD_NAMES.AWS_STORAGE.AWS_SECRET_ACCESS_KEY_FIELD_NAME]: "",
          [FIELD_NAMES.AWS_STORAGE.BUCKET_NAME_FIELD_NAME]: bucket,
          [FIELD_NAMES.AWS_STORAGE.S3_PATH_FIELD_NAME]: s3Prefix
        }
      : {}),
    ...(type === BI_EXPORT_STORAGE_TYPE.AZURE_RAW_EXPORT
      ? {
          [FIELD_NAMES.AZURE_STORAGE.CONNECTION_STRING_FIELD_NAME]: "",
          [FIELD_NAMES.AZURE_STORAGE.CONTAINER_FIELD_NAME]: container
        }
      : {})
  };
};
