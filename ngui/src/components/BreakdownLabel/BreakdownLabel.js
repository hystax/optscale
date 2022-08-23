import React from "react";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import CloudLabel from "components/CloudLabel";
import PoolLabel from "components/PoolLabel";
import { RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY, RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY_VALUES } from "utils/constants";

const getIdText = (details) => (details.id === "null" ? <FormattedMessage id="(not set)" /> : details.id);

const getLabelText = (details) => details.name || getIdText(details);

const BreakdownLabel = ({ breakdownBy, details }) => {
  const getLabel = () => getLabelText(details);

  const renderer = {
    [RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.EMPLOYEE_ID]: () => getLabel(),
    [RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.POOL_ID]: () => <PoolLabel type={details.purpose} label={getLabel()} />,
    [RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.CLOUD_ACCOUNT_ID]: () => <CloudLabel type={details.type} label={getLabel()} />,
    [RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.SERVICE_NAME]: () => getLabel(),
    [RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.REGION]: () => getLabel(),
    [RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.RESOURCE_TYPE]: () => getLabel(),
    [RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.K8S_NODE]: () => getLabel(),
    [RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.K8S_NAMESPACE]: () => getLabel(),
    [RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.K8S_SERVICE]: () => getLabel()
  }[breakdownBy];

  return renderer();
};

BreakdownLabel.propTypes = {
  breakdownBy: PropTypes.oneOf(RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY_VALUES).isRequired,
  details: PropTypes.shape({
    id: PropTypes.string,
    name: PropTypes.string,
    type: PropTypes.string,
    purpose: PropTypes.string
  })
};

export default BreakdownLabel;
