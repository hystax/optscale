import CloudLabel from "components/CloudLabel";
import PoolLabel from "components/PoolLabel";
import { intl } from "translations/react-intl-config";
import { RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY } from "utils/constants";

const getIdText = (details) => (details.id === "null" ? intl.formatMessage({ id: "(not set)" }) : details.id);

export const getBreakdownLabelText = (details) => details.name || getIdText(details);

const BreakdownLabel = ({ breakdownBy, details }) => {
  const getLabel = () => getBreakdownLabelText(details);

  const renderer = {
    [RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.EMPLOYEE_ID]: () => getLabel(),
    [RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.POOL_ID]: () => <PoolLabel type={details.purpose} label={getLabel()} />,
    [RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.CLOUD_ACCOUNT_ID]: () => <CloudLabel type={details.type} label={getLabel()} />,
    [RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.SERVICE_NAME]: () => getLabel(),
    [RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.REGION]: () => getLabel(),
    [RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.RESOURCE_TYPE]: () => getLabel(),
    [RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.K8S_NODE]: () => getLabel(),
    [RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.K8S_NAMESPACE]: () => getLabel(),
    [RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.K8S_SERVICE]: () => getLabel(),
  }[breakdownBy];

  return renderer();
};

export default BreakdownLabel;
