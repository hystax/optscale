import React from "react";
import CancelIcon from "@mui/icons-material/Cancel";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import PlayCircleIcon from "@mui/icons-material/PlayCircle";
import StopCircleOutlinedIcon from "@mui/icons-material/StopCircleOutlined";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import IconLabel from "components/IconLabel";
import { ML_RUN_STATUS } from "utils/constants";

export const MlRunStatusLabel = ({ status }) => {
  const labelMessageId = {
    [ML_RUN_STATUS.STOPPED]: "stopped",
    [ML_RUN_STATUS.ABORTED]: "aborted",
    [ML_RUN_STATUS.RUNNING]: "running",
    [ML_RUN_STATUS.COMPLETED]: "completed",
    [ML_RUN_STATUS.FAILED]: "failed"
  }[status];

  return <FormattedMessage id={labelMessageId} />;
};

export const MlRunStatusIcon = ({ status, iconSize = "small" }) => {
  const icon = {
    [ML_RUN_STATUS.STOPPED]: <StopCircleOutlinedIcon fontSize={iconSize} color="primary" />,
    [ML_RUN_STATUS.ABORTED]: <StopCircleOutlinedIcon fontSize={iconSize} color="info" />,
    [ML_RUN_STATUS.COMPLETED]: <CheckCircleIcon fontSize={iconSize} color="success" />,
    [ML_RUN_STATUS.RUNNING]: <PlayCircleIcon fontSize={iconSize} color="primary" />,
    [ML_RUN_STATUS.FAILED]: <CancelIcon fontSize={iconSize} color="error" />
  }[status];

  return icon;
};

const MlRunStatus = ({ status, iconSize }) => (
  <IconLabel icon={<MlRunStatusIcon status={status} iconSize={iconSize} />} label={<MlRunStatusLabel status={status} />} />
);

MlRunStatus.propTypes = {
  status: PropTypes.oneOf(Object.values(ML_RUN_STATUS)).isRequired,
  iconSize: PropTypes.string
};

export default MlRunStatus;
