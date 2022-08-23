import React from "react";
import { FormattedMessage } from "react-intl";
import AnomalyRunChartCell from "components/AnomalyRunChartCell";
import TextWithDataTestId from "components/TextWithDataTestId";
import { isEmpty } from "utils/objects";

const anomalyStatusChart = ({ constraint, headerMessageId = "statusAtHit", todayMessageId = "hit" }) => ({
  Header: (
    <TextWithDataTestId dataTestId="lbl_status">
      <FormattedMessage id={headerMessageId} />
    </TextWithDataTestId>
  ),
  accessor: "run_result",
  Cell: ({ cell: { value } }) => {
    if (!value || isEmpty(value)) {
      return "-";
    }

    const { breakdown, today, average } = value;

    return (
      <AnomalyRunChartCell
        breakdown={breakdown}
        today={today}
        average={average}
        threshold={constraint.definition.threshold}
        type={constraint.type}
        todayMessageId={todayMessageId}
      />
    );
  }
});

export default anomalyStatusChart;
