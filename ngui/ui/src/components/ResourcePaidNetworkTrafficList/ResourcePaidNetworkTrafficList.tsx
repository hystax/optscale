import { Stack } from "@mui/material";
import { FormattedMessage } from "react-intl";
import DashedTypography from "components/DashedTypography";
import FromToArrowLabel from "components/FromToArrowLabel";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import PaidNetworkTrafficLabel from "components/PaidNetworkTrafficLabel";
import { useToggle } from "hooks/useToggle";
import { sortObjects, isEmpty as isEmptyArray, splitIntoTwoChunks } from "utils/arrays";
import { SPACING_1 } from "utils/layouts";

const EXPENSE_THRESHOLD = 1;

const ELEMENTS_COUNT_LIMIT = 5;

export const getTrafficExpensesDataChunks = (trafficExpenses) => {
  if (isEmptyArray(trafficExpenses)) {
    return {
      expensesChunk1: [],
      expensesChunk2: []
    };
  }

  const trafficExpensesSorted = sortObjects({
    array: trafficExpenses,
    field: "cost",
    type: "desc"
  });

  const getSplitIndex = () => {
    const thresholdIndex = trafficExpensesSorted.findIndex(({ cost }) => cost < EXPENSE_THRESHOLD);

    return thresholdIndex !== -1 && thresholdIndex < ELEMENTS_COUNT_LIMIT
      ? thresholdIndex || 1
      : Math.min(trafficExpensesSorted.length, ELEMENTS_COUNT_LIMIT);
  };

  const splitIndex = getSplitIndex();

  const [expensesChunk1, expensesChunk2] = splitIntoTwoChunks(trafficExpensesSorted, splitIndex);

  return {
    expensesChunk1,
    expensesChunk2
  };
};

const ResourcePaidNetworkTrafficList = ({ trafficExpenses = [] }) => {
  const [isExpanded, toggle] = useToggle(false);

  if (isEmptyArray(trafficExpenses)) {
    return null;
  }

  const { expensesChunk1, expensesChunk2 } = getTrafficExpensesDataChunks(trafficExpenses);

  return (
    <>
      <Stack spacing={SPACING_1}>
        {(isExpanded ? [...expensesChunk1, ...expensesChunk2] : expensesChunk1).map(({ from, to, cost, usage }) => (
          <KeyValueLabel
            key={`${from}-${to}`}
            keyText={<FromToArrowLabel from={from} to={to} />}
            value={<PaidNetworkTrafficLabel cost={cost} usage={usage} />}
            isBoldValue={false}
          />
        ))}
      </Stack>
      <DashedTypography onClick={toggle}>
        {!isExpanded && !isEmptyArray(expensesChunk2) && <FormattedMessage id="showMore" />}
        {isExpanded && <FormattedMessage id="showLess" />}
      </DashedTypography>
    </>
  );
};

export default ResourcePaidNetworkTrafficList;
