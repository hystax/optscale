import ExportedDaysField, { FIELD_NAME as EXPORTED_DAYS_FIELD_NAME } from "./ExportedDaysField";
import FormButtons from "./FormButtons";
import NameField, { FIELD_NAME as NAME_FIELD_NAME } from "./NameField";
import AwsAccessKeyIdField, { FIELD_NAME as AWS_ACCESS_KEY_ID_FIELD_NAME } from "./StorageTypeFields/AWS/AwsAccessKeyIdField";
import AwsSecretAccessKeyField, {
  FIELD_NAME as AWS_SECRET_ACCESS_KEY_FIELD_NAME
} from "./StorageTypeFields/AWS/AwsSecretAccessKeyField";
import BucketNameField, { FIELD_NAME as BUCKET_NAME_FIELD_NAME } from "./StorageTypeFields/AWS/BucketNameField";
import S3PrefixField, { FIELD_NAME as S3_PATH_FIELD_NAME } from "./StorageTypeFields/AWS/S3PrefixField";
import ConnectionStringField, {
  FIELD_NAME as CONNECTION_STRING_FIELD_NAME
} from "./StorageTypeFields/Azure/ConnectionStringField";
import ContainerField, { FIELD_NAME as CONTAINER_FIELD_NAME } from "./StorageTypeFields/Azure/ContainerField";
import StorageTypeSelectorField, { FIELD_NAME as STORAGE_TYPE_FIELD_NAME } from "./StorageTypeSelectorField";

const FIELD_NAMES = Object.freeze({
  STORAGE_TYPE_FIELD_NAME,
  NAME_FIELD_NAME,
  EXPORTED_DAYS_FIELD_NAME,
  AWS_ACCESS_KEY_ID_FIELD_NAME,
  AWS_SECRET_ACCESS_KEY_FIELD_NAME,
  BUCKET_NAME_FIELD_NAME,
  S3_PATH_FIELD_NAME,
  CONNECTION_STRING_FIELD_NAME,
  CONTAINER_FIELD_NAME
});

export {
  StorageTypeSelectorField,
  NameField,
  ExportedDaysField,
  AwsAccessKeyIdField,
  AwsSecretAccessKeyField,
  BucketNameField,
  S3PrefixField,
  ConnectionStringField,
  ContainerField,
  FormButtons,
  FIELD_NAMES
};
