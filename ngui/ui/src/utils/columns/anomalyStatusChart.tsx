import { FormattedMessage } from "react-intl";
import AnomalyRunChartCell from "components/AnomalyRunChartCell";
import TextWithDataTestId from "components/TextWithDataTestId";
import { isEmptyObject } from "utils/objects";

const anomalyStatusChart = ({ constraint, headerMessageId = "statusAtHit", todayMessageId = "hit" }) => ({
  header: (
    <TextWithDataTestId dataTestId="lbl_status">
      <FormattedMessage id={headerMessageId} />
    </TextWithDataTestId>
  ),
  accessorKey: "run_result",
  cell: ({ cell }) => {
    const value = cell.getValue();

    if (!value || isEmptyObject(value)) {
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
  },
});

export default anomalyStatusChart;
