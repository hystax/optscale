export const BILLING_IMPORT_STATUS = Object.freeze({
  SUCCESS: "success",
  ERROR: "error",
  UNKNOWN: "unknown"
});

export const getBillingImportStatus = ({ timestamp, attemptTimestamp, error }) => {
  if (timestamp > 0 && timestamp === attemptTimestamp) {
    return BILLING_IMPORT_STATUS.SUCCESS;
  }
  if (error && timestamp < attemptTimestamp) {
    return BILLING_IMPORT_STATUS.ERROR;
  }

  return BILLING_IMPORT_STATUS.UNKNOWN;
};
