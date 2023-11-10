export const STATUS = Object.freeze({
  CREATED: "CREATED",
  RUNNING: "RUNNING",
  FAILED: "FAILED",
  SUCCESS: "SUCCESS",
  QUEUED: "QUEUED"
});

const COLORS = Object.freeze({
  [STATUS.CREATED]: "info",
  [STATUS.QUEUED]: "info",
  [STATUS.SUCCESS]: "success",
  [STATUS.RUNNING]: "primary",
  [STATUS.FAILED]: "error"
});

export const getStatusColor = (status) => COLORS[status];
