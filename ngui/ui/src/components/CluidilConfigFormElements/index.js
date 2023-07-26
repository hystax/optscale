import AccessKeyTitle from "./AccessKeyTitle";
import AuthorizedKeyTitle from "./AuthorizedKeyTitle";
import BillingReportBucketDescription from "./BillingReportBucketDescription";
import BillingReportBucketTitle from "./BillingReportBucketTitle";
import AccessKeyId, { FIELD_NAME as ACCESS_KEY_ID } from "./Fields/AccessKeyId";
import AccessKeySecretKey, { FIELD_NAME as SECRET_ACCESS_KEY } from "./Fields/AccessKeySecretKey";
import AuthorizedKeyId, { FIELD_NAME as KEY_ID } from "./Fields/AuthorizedKeyId";
import AuthorizedKeyPrivateKey, { FIELD_NAME as PRIVATE_KEY } from "./Fields/AuthorizedKeyPrivateKey";
import CloudName, { FIELD_NAME as CLOUD_NAME } from "./Fields/CloudName";
import ReportBucketName, { FIELD_NAME as BUCKET_NAME } from "./Fields/ReportBucketName";
import ReportBucketPathPrefix, { FIELD_NAME as BUCKET_PREFIX } from "./Fields/ReportBucketPathPrefix";
import ServiceAccountId, { FIELD_NAME as SERVICE_ACCOUNT_ID } from "./Fields/ServiceAccountId";
import ServiceAccountCredentialsDescription from "./ServiceAccountCredentialsDescription";

const FIELD_NAMES = {
  CLOUD_NAME,
  SERVICE_ACCOUNT_ID,
  KEY_ID,
  PRIVATE_KEY,
  ACCESS_KEY_ID,
  SECRET_ACCESS_KEY,
  BUCKET_NAME,
  BUCKET_PREFIX
};

export {
  FIELD_NAMES,
  CloudName,
  ServiceAccountCredentialsDescription,
  ServiceAccountId,
  AuthorizedKeyTitle,
  AuthorizedKeyId,
  AuthorizedKeyPrivateKey,
  AccessKeyTitle,
  AccessKeyId,
  AccessKeySecretKey,
  BillingReportBucketTitle,
  BillingReportBucketDescription,
  ReportBucketName,
  ReportBucketPathPrefix
};
