import React from "react";
import PropTypes from "prop-types";
import FormattedMoney from "components/FormattedMoney";
import HeartLineChart from "components/HeartLineChart";
import KeyValueLabel from "components/KeyValueLabel";
import Tooltip from "components/Tooltip";
import { EXPENSE_ANOMALY } from "utils/constants";

const AnomalyRunChartCell = ({ breakdown, today, average, threshold, type, todayMessageId = "today" }) => {
  const width = 160;
  const height = 20;

  const onlyValues = Object.values(breakdown);
  onlyValues.push(today);

  const getFormattedValue = (value) => (type === EXPENSE_ANOMALY ? <FormattedMoney value={value} /> : Math.round(value));

  return (
    <Tooltip
      title={
        <>
          <KeyValueLabel messageId="average" value={getFormattedValue(average)} />
          <KeyValueLabel messageId={todayMessageId} value={getFormattedValue(today)} />
        </>
      }
    >
      <HeartLineChart
        values={onlyValues}
        redZoneValue={average * (1 + threshold / 100)}
        average={average}
        width={width}
        height={height}
      />
    </Tooltip>
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
