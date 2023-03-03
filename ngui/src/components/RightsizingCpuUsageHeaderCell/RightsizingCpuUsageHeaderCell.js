import React from "react";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import HeaderHelperCell from "components/HeaderHelperCell";
import TextWithDataTestId from "components/TextWithDataTestId";
import { isEmpty as isEmptyObject } from "utils/objects";

const RightsizingCpuUsageHeaderCell = ({ options = {} }) =>
  isEmptyObject ? (
    <TextWithDataTestId dataTestId="lbl_rightsizing_instance_cpu_usage_percent">
      <FormattedMessage id="cpuUsage" />
    </TextWithDataTestId>
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
