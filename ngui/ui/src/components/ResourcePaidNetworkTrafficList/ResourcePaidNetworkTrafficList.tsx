import ExpandableList from "components/ExpandableList";
import FromToArrowLabel from "components/FromToArrowLabel";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import PaidNetworkTrafficLabel from "components/PaidNetworkTrafficLabel";
import { sortObjects } from "utils/arrays";

const EXPENSE_THRESHOLD = 1;

const ELEMENTS_COUNT_LIMIT = 5;

const getMaxRows = (trafficExpensesSorted) => {
  const thresholdIndex = trafficExpensesSorted.findIndex(({ cost }) => cost < EXPENSE_THRESHOLD);

  return thresholdIndex !== -1 && thresholdIndex < ELEMENTS_COUNT_LIMIT
    ? thresholdIndex || 1
    : Math.min(trafficExpensesSorted.length, ELEMENTS_COUNT_LIMIT);
};

const ResourcePaidNetworkTrafficList = ({ trafficExpenses = [] }) => {
  const trafficExpensesSorted = sortObjects({
    array: trafficExpenses,
    field: "cost",
    type: "desc"
  });

  return (
    <ExpandableList
      items={trafficExpensesSorted}
      render={(item) => {
        const { from, to, cost, usage } = item;

        return (
          <KeyValueLabel
            key={`${from}-${to}`}
            keyText={<FromToArrowLabel from={from} to={to} />}
            value={<PaidNetworkTrafficLabel cost={cost} usage={usage} />}
            isBoldValue={false}
            gutterBottom
          />
        );
      }}
      maxRows={getMaxRows(trafficExpensesSorted)}
    />
  );
};

export default ResourcePaidNetworkTrafficList;
