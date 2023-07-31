import React from "react";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import MlRunStatus from "components/MlRunStatus";
import { ML_MODEL_STATUS } from "utils/constants";

const MlModelStatus = ({ status, iconSize }) =>
  status === ML_MODEL_STATUS.CREATED ? <FormattedMessage id="created" /> : <MlRunStatus status={status} iconSize={iconSize} />;

MlModelStatus.propTypes = {
  status: PropTypes.oneOf(Object.values(ML_MODEL_STATUS)).isRequired,
  iconSize: PropTypes.string
};

export default MlModelStatus;
