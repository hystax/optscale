import React from "react";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import Selector from "components/Selector";
import { RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY, RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY_VALUES } from "utils/constants";

const selectorItems = [
  {
    value: RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.SERVICE_NAME,
    name: <FormattedMessage id="service" />
  },
  {
    value: RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.REGION,
    name: <FormattedMessage id="region" />
  },
  {
    value: RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.RESOURCE_TYPE,
    name: <FormattedMessage id="resourceType" />
  },
  {
    value: RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.CLOUD_ACCOUNT_ID,
    name: <FormattedMessage id="dataSource" />
  },
  {
    value: RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.EMPLOYEE_ID,
    name: <FormattedMessage id="owner" />
  },
  {
    value: RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.POOL_ID,
    name: <FormattedMessage id="pool" />
  },
  {
    value: RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.K8S_NODE,
    name: <FormattedMessage id="k8sNode" />
  },
  {
    value: RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.K8S_NAMESPACE,
    name: <FormattedMessage id="k8sNamespace" />
  },
  {
    value: RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.K8S_SERVICE,
    name: <FormattedMessage id="k8sService" />
  }
];

const BreakdownBy = ({ value, onChange }) => (
  <Selector
    data={{
      selected: value,
      items: selectorItems
    }}
    labelId="categorizeBy"
    onChange={onChange}
  />
);

BreakdownBy.propTypes = {
  value: PropTypes.oneOf(RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY_VALUES).isRequired,
  onChange: PropTypes.func.isRequired
};

export default BreakdownBy;
