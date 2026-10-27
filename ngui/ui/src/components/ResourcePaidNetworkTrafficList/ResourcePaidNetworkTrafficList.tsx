import { Typography } from "@mui/material";
import { useIntl } from "react-intl";
import ExpandableList from "components/ExpandableList";
import { formatDigitalUnit, SI_UNITS } from "components/FormattedDigitalUnit";
import { useMoneyFormatter } from "components/FormattedMoney";
import { sortObjects } from "utils/arrays";
import { FORMATTED_MONEY_TYPES } from "utils/constants";

const EXPENSE_THRESHOLD = 1;

const ELEMENTS_COUNT_LIMIT = 5;

const getMaxRows = (trafficExpensesSorted) => {
  const thresholdIndex = trafficExpensesSorted.findIndex(({ cost }) => cost < EXPENSE_THRESHOLD);

  return thresholdIndex !== -1 && thresholdIndex < ELEMENTS_COUNT_LIMIT
    ? thresholdIndex || 1
    : Math.min(trafficExpensesSorted.length, ELEMENTS_COUNT_LIMIT);
};

const TrafficLabel = ({ from, to, cost, usage }) => {
  const intl = useIntl();
  const moneyFormatter = useMoneyFormatter();

  const fromTo = intl.formatMessage({ id: "value -> value" }, { value1: from, value2: to });
  const money = moneyFormatter(FORMATTED_MONEY_TYPES.COMMON, cost);
  const usageFormatted = formatDigitalUnit({ value: usage, baseUnit: SI_UNITS.GIGABYTE });

  const label = intl.formatMessage({ id: "value: value" }, { value1: fromTo, value2: `${money} / ${usageFormatted}` });

  return <Typography gutterBottom>{label}</Typography>;
};

const ResourcePaidNetworkTrafficList = ({ trafficExpenses = [] }) => {
  const trafficExpensesSorted = sortObjects({
    array: trafficExpenses,
    field: "cost",
    type: "desc",
  });

  return (
    <ExpandableList
      items={trafficExpensesSorted}
      render={(item) => {
        const { from, to, cost, usage } = item;
        return <TrafficLabel key={`${from}-${to}-${cost}-${usage}`} from={from} to={to} cost={cost} usage={usage} />;
      }}
      maxRows={getMaxRows(trafficExpensesSorted)}
    />
  );
};

export default ResourcePaidNetworkTrafficList;
