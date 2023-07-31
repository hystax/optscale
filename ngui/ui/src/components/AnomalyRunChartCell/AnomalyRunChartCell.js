import React from "react";
import PropTypes from "prop-types";
import FormattedMoney from "components/FormattedMoney";
import HeartLineChart from "components/HeartLineChart";
import KeyValueLabel from "components/KeyValueLabel";
import { EXPENSE_ANOMALY } from "utils/constants";
import { CELL_EMPTY_VALUE } from "utils/tables";

const AnomalyRunChartCell = ({ breakdown, today, average, threshold, type, todayMessageId = "today" }) => {
  const onlyValues = Object.values(breakdown);
  onlyValues.push(today);

  const getFormattedValue = (value) => (type === EXPENSE_ANOMALY ? <FormattedMoney value={value} /> : Math.round(value));

  return onlyValues.length < 2 ? (
    CELL_EMPTY_VALUE
  ) : (
    <HeartLineChart
      values={onlyValues}
      width={160}
      height={40}
      tooltip={
        <>
          <KeyValueLabel messageId="average" value={getFormattedValue(average)} />
          <KeyValueLabel messageId={todayMessageId} value={getFormattedValue(today)} />
        </>
      }
      thresholdArea={{
        start: average,
        end: average * (1 + threshold / 100)
      }}
    />
  );
};

AnomalyRunChartCell.propTypes = {
  breakdown: PropTypes.object.isRequired,
  today: PropTypes.number.isRequired,
  average: PropTypes.number.isRequired,
  threshold: PropTypes.number.isRequired,
  type: PropTypes.string.isRequired,
  todayMessageId: PropTypes.string
};

export default AnomalyRunChartCell;
