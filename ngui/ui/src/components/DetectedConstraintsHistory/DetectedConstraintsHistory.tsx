import { FormattedMessage } from "react-intl";
import DetectedConstraintsHistoryTable from "components/DetectedConstraintsHistoryTable";
import SubTitle from "components/SubTitle";
import TableLoader from "components/TableLoader";
import TypographyLoader from "components/TypographyLoader";
import { isEmpty as isEmptyArray } from "utils/arrays";
import {
  EXPENSE_ANOMALY,
  EXPIRING_BUDGET_POLICY,
  QUOTA_POLICY,
  RECURRING_BUDGET_POLICY,
  TAGGING_POLICY,
  RESOURCE_COUNT_ANOMALY
} from "utils/constants";

const mapConstraintTypeToTitleMessageId = (type) => {
  const detectedAnomaliesHistoryTitle = "detectedAnomaliesHistory";
  const policyViolationsHistoryTitle = "policyViolationsHistory";

  return (
    {
      [EXPENSE_ANOMALY]: detectedAnomaliesHistoryTitle,
      [RESOURCE_COUNT_ANOMALY]: detectedAnomaliesHistoryTitle,
      [QUOTA_POLICY]: policyViolationsHistoryTitle,
      [RECURRING_BUDGET_POLICY]: policyViolationsHistoryTitle,
      [EXPIRING_BUDGET_POLICY]: policyViolationsHistoryTitle,
      [TAGGING_POLICY]: policyViolationsHistoryTitle
    }[type] ?? detectedAnomaliesHistoryTitle
  );
};

const DetectedConstraintsHistory = ({ limitHits, constraint, isLoading = false }) => {
  if (isLoading) {
    return (
      <>
        <TypographyLoader />
        <TableLoader columnsCounter={3} />
      </>
    );
  }

  if (isEmptyArray(limitHits)) {
    return null;
  }

  return (
    <>
      <SubTitle>
        <FormattedMessage id={mapConstraintTypeToTitleMessageId(constraint?.type)} />
      </SubTitle>
      <DetectedConstraintsHistoryTable limitHits={limitHits} constraint={constraint} />
    </>
  );
};

export default DetectedConstraintsHistory;
