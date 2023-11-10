import { FormattedMessage } from "react-intl";
import DetectedConstraintsHistoryTable from "components/DetectedConstraintsHistoryTable";
import SubTitle from "components/SubTitle";
import TableLoader from "components/TableLoader";
import OrganizationsLimitHitsService from "services/OrganizationsLimitHitsService";
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

const HistorySection = ({ children, type }) => (
  <>
    <SubTitle>
      <FormattedMessage id={mapConstraintTypeToTitleMessageId(type)} />
    </SubTitle>
    {children}
  </>
);

const DetectedConstraintsHistoryContainer = ({ constraint, isGetConstraintLoading = false }) => {
  const { useGet } = OrganizationsLimitHitsService();

  const { isLoading, data } = useGet(constraint.id);

  if (isLoading || isGetConstraintLoading) {
    return (
      <HistorySection>
        <TableLoader columnsCounter={3} />
      </HistorySection>
    );
  }

  if (isEmptyArray(data)) {
    return null;
  }

  return (
    <HistorySection type={constraint.type}>
      <DetectedConstraintsHistoryTable limitHits={data} constraint={constraint} />
    </HistorySection>
  );
};

export default DetectedConstraintsHistoryContainer;
