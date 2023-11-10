import CancelIcon from "@mui/icons-material/Cancel";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";

export const BI_EXPORT_STATUSES = Object.freeze({
  NONE: "none",
  FAILED: "failed",
  COMPLETED: "completed"
});

export const BI_EXPORT_ACTIVITY_STATUSES = Object.freeze({
  QUEUED: "queued",
  RUNNING: "running",
  IDLE: "idle"
});

export const getBIExportStatus = (biExport) => {
  if (biExport.last_completed === 0 && !biExport.last_status_error) {
    return BI_EXPORT_STATUSES.NONE;
  }
  if (biExport.last_status_error) {
    return BI_EXPORT_STATUSES.FAILED;
  }
  return BI_EXPORT_STATUSES.COMPLETED;
};

export const getBIExportActivityStatus = (status) => BI_EXPORT_ACTIVITY_STATUSES[status] || BI_EXPORT_ACTIVITY_STATUSES.IDLE;

export const BI_EXPORT_STORAGE_TYPE = Object.freeze({
  AWS_RAW_EXPORT: "AWS_RAW_EXPORT",
  AZURE_RAW_EXPORT: "AZURE_RAW_EXPORT"
});

export const getBIExportStatusIconSettings = (status) =>
  ({
    [BI_EXPORT_STATUSES.COMPLETED]: {
      Icon: CheckCircleIcon,
      color: "success",
      messageId: "completed"
    },
    [BI_EXPORT_STATUSES.FAILED]: {
      Icon: CancelIcon,
      color: "error",
      messageId: "failed"
    }
  })[status];
