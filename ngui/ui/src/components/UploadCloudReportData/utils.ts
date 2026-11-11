import { FOCUS } from "utils/constants";

const FILE_TYPES = [
  "application/gzip",
  "application/x-gzip",
  "application/zip",
  "application/x-zip-compressed",
  // Archives reported with another MIME type are accepted by the extension (.gz covers .csv.gz)
  ".gz",
  ".zip",
  "",
  "text/csv",
  ".csv",
];

const PARQUET_FILE_TYPES = ["application/vnd.apache.parquet", ".parquet"];

// Only FOCUS reports can be uploaded as Parquet files
export const getAcceptedFileTypes = (dataSourceType: string) =>
  dataSourceType === FOCUS ? [...FILE_TYPES, ...PARQUET_FILE_TYPES] : FILE_TYPES;
