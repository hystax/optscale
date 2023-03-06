import React from "react";
import CancelIcon from "@mui/icons-material/Cancel";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import PlayCircleIcon from "@mui/icons-material/PlayCircle";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import IconLabel from "components/IconLabel";
import { ML_RUN_STATUS } from "utils/constants";

export const MlRunStatusLabel = ({ status }) => {
  const labelMessageId = {
    [ML_RUN_STATUS.RUNNING]: "running",
    [ML_RUN_STATUS.COMPLETED]: "completed",
    [ML_RUN_STATUS.FAILED]: "failed"
  }[status];

  return <FormattedMessage id={labelMessageId} />;
};

const MlRunStatusIcon = ({ status }) => {
  const icon = {
    [ML_RUN_STATUS.COMPLETED]: <CheckCircleIcon fontSize="small" color="success" />,
    [ML_RUN_STATUS.RUNNING]: <PlayCircleIcon fontSize="small" color="primary" />,
    [ML_RUN_STATUS.FAILED]: <CancelIcon fontSize="small" color="error" />
  }[status];

  return icon;
};

const MlRunStatus = ({ status }) => (
  <IconLabel icon={<MlRunStatusIcon status={status} />} label={<MlRunStatusLabel status={status} />} />
);

MlRunStatus.propTypes = {
  status: PropTypes.oneOf(Object.values(ML_RUN_STATUS))
};

export default MlRunStatus;
