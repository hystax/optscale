import { BI_EXPORT_STORAGE_TYPE } from "utils/biExport";
import { FIELD_NAMES } from "./constants";

type StorageType = (typeof BI_EXPORT_STORAGE_TYPE)[keyof typeof BI_EXPORT_STORAGE_TYPE];

type AwsRawExportMeta = {
  access_key_id: string;
  secret_access_key: string;
  bucket: string;
  s3_prefix: string | undefined;
};

type AzureRawExportMeta = {
  connection_string: string;
  container: string;
};

type AwsRawExport = {
  type: typeof BI_EXPORT_STORAGE_TYPE.AWS_RAW_EXPORT;
  meta: AwsRawExportMeta;
};

type AzureRawExport = {
  type: typeof BI_EXPORT_STORAGE_TYPE.AZURE_RAW_EXPORT;
  meta: AzureRawExportMeta;
};

export type ExportType = AwsRawExport | AzureRawExport;

type SubmitData = {
  name: string;
  days: number;
  meta: AwsRawExportMeta | AzureRawExportMeta;
  type?: StorageType;
};

export type FormValues = {
  [FIELD_NAMES.NAME]: string;
  [FIELD_NAMES.EXPORTED_DAYS]: string;
  [FIELD_NAMES.STORAGE_TYPE]: StorageType;
  [FIELD_NAMES.AWS_STORAGE.AWS_ACCESS_KEY_ID_FIELD_NAME]: string;
  [FIELD_NAMES.AWS_STORAGE.AWS_SECRET_ACCESS_KEY_FIELD_NAME]: string;
  [FIELD_NAMES.AWS_STORAGE.BUCKET_NAME_FIELD_NAME]: string;
  [FIELD_NAMES.AWS_STORAGE.S3_PATH_FIELD_NAME]: string;
  [FIELD_NAMES.AZURE_STORAGE.CONNECTION_STRING_FIELD_NAME]: string;
  [FIELD_NAMES.AZURE_STORAGE.CONTAINER_FIELD_NAME]: string;
};
export type BIExportFormProps = {
  defaultValues: FormValues;
  isLoadingProps: {
    isSubmitLoading: boolean;
    isGetDataLoading: boolean;
  };
  onSubmit: (params: SubmitData) => void;
  onCancel: () => void;
  isEdit?: boolean;
};
