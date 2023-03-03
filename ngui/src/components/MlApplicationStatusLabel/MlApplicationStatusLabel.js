import React from "react";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { MlRunStatusLabel } from "components/MlRunStatus";
import { ML_APPLICATION_STATUS } from "utils/constants";

const MlApplicationStatusLabel = ({ status }) =>
  status === ML_APPLICATION_STATUS.CREATED ? <FormattedMessage id="created" /> : <MlRunStatusLabel status={status} />;

MlApplicationStatusLabel.propTypes = {
  status: PropTypes.oneOf(Object.values(ML_APPLICATION_STATUS))
};

export default MlApplicationStatusLabel;
