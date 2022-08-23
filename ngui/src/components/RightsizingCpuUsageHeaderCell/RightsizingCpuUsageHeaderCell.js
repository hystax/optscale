import React from "react";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import HeaderHelperCell from "components/HeaderHelperCell";
import { isEmpty as isEmptyObject } from "utils/objects";

const RightsizingCpuUsageHeaderCell = ({ options = {} }) =>
  isEmptyObject ? (
    <FormattedMessage id="cpuUsage" />
  ) : (
    <HeaderHelperCell
      titleDataTestId="lbl_rightsizing_instance_cpu_usage_percent"
      titleMessageId="cpuUsage"
      helperMessageId="rightsizingCPUUsage"
      helperMessageValues={{ days: options.days_threshold }}
    />
  );

RightsizingCpuUsageHeaderCell.propTypes = {
  options: PropTypes.object
};

export default RightsizingCpuUsageHeaderCell;
