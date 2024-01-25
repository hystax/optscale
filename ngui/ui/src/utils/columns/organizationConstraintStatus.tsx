import CancelIcon from "@mui/icons-material/Cancel";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import { Box } from "@mui/material";
import { FormattedMessage } from "react-intl";
import AnomalyRunChartCell from "components/AnomalyRunChartCell";
import FormattedMoney from "components/FormattedMoney";
import ProgressBar from "components/ProgressBar";
import TextWithDataTestId from "components/TextWithDataTestId";
import { QUOTA_POLICY, FORMATTED_MONEY_TYPES } from "utils/constants";
import { getPoolColorStatus } from "utils/layouts";
import {
  hasStatusInformation,
  isAnomalyConstraint,
  isQuotasAndBudgetsConstraint,
  isTaggingPolicyConstraint
} from "utils/organizationConstraints";

const ConstraintStatusCell = ({ constraint }) => {
  const { last_run_result: lastRunResult = {}, definition, type } = constraint;

  switch (true) {
    case !hasStatusInformation(constraint): {
      return <FormattedMessage id="noStatusInformationYet" />;
    }
    case isAnomalyConstraint(type): {
      const { breakdown = {}, average = 0, today = 0 } = lastRunResult;

      return (
        <AnomalyRunChartCell
          breakdown={breakdown}
          today={today}
          average={average}
          threshold={definition.threshold}
          type={type}
        />
      );
    }
    case isQuotasAndBudgetsConstraint(type): {
      const { current, limit } = lastRunResult;
      const xDividedByY = current / limit;
      const percent = xDividedByY * 100;

      const label = type === QUOTA_POLICY ? current : <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={current} />;
      return (
        <ProgressBar color={getPoolColorStatus(percent)} value={percent} wrapperSx={{ minWidth: "160px" }}>
          {label}
        </ProgressBar>
      );
    }
    case isTaggingPolicyConstraint(type): {
      const { value: violations } = lastRunResult;

      return (
        <Box display="flex" alignItems="center">
          {violations === 0 ? (
            <CheckCircleIcon fontSize="small" color="success" />
          ) : (
            <>
              <CancelIcon fontSize="small" color="error" />
              <FormattedMessage id="violationsRightNow" values={{ value: violations }} />
            </>
          )}
        </Box>
      );
    }
    default:
      return null;
  }
};

const organizationConstraintStatus = () => ({
  header: (
    <TextWithDataTestId dataTestId="lbl_status">
      <FormattedMessage id="status" />
    </TextWithDataTestId>
  ),
  id: "status",
  cell: ({ row }) => <ConstraintStatusCell constraint={row.original} />,
  enableSorting: false,
  enableGlobalFilter: false
});

export default organizationConstraintStatus;
