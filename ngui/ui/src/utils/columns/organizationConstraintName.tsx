import ErrorOutlineIcon from "@mui/icons-material/ErrorOutline";
import Link from "@mui/material/Link";
import { FormattedMessage, useIntl } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import CaptionedCell from "components/CaptionedCell";
import IconLabel from "components/IconLabel";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import SlicedText from "components/SlicedText";
import TextWithDataTestId from "components/TextWithDataTestId";
import Tooltip from "components/Tooltip";
import { useIntervalTimeAgo } from "hooks/useIntervalTimeAgo";
import { getAnomalyUrl, getQuotaAndBudgetUrl, getTaggingPolicyUrl } from "urls";
import { ANOMALY_TYPES, QUOTAS_AND_BUDGETS_TYPES, TAGGING_POLICY_TYPES } from "utils/constants";
import { isAnomalyConstraint, isQuotasAndBudgetsConstraint, isTaggingPolicyConstraint } from "utils/organizationConstraints";

type ConstraintType = keyof typeof ANOMALY_TYPES | keyof typeof TAGGING_POLICY_TYPES | keyof typeof QUOTAS_AND_BUDGETS_TYPES;
type NameCellProps = {
  lastRun: number;
  limitHitsCount: number;
  id: string;
  type: ConstraintType;
  name: string;
};

const getLink = (id: string, type: ConstraintType) => {
  switch (true) {
    case isAnomalyConstraint(type): {
      return getAnomalyUrl(id);
    }
    case isQuotasAndBudgetsConstraint(type): {
      return getQuotaAndBudgetUrl(id);
    }
    case isTaggingPolicyConstraint(type): {
      return getTaggingPolicyUrl(id);
    }
    default:
      return null;
  }
};

const NameCell = ({ lastRun, limitHitsCount, id, type, name }: NameCellProps) => {
  const timeAgo = useIntervalTimeAgo(lastRun, 1);
  const intl = useIntl();

  return (
    <CaptionedCell
      caption={{
        key: "lastRunCaption",
        node: lastRun ? (
          <IconLabel
            icon={
              limitHitsCount !== 0 && (
                <Tooltip title={intl.formatMessage({ id: "hitsForLastDays" }, { value: limitHitsCount, amount: 3 })}>
                  <ErrorOutlineIcon fontSize="inherit" />
                </Tooltip>
              )
            }
            label={<KeyValueLabel keyMessageId="lastCheck" value={timeAgo} variant="caption" />}
            component={RouterLink}
          />
        ) : null
      }}
    >
      <Link to={getLink(id, type)} component={RouterLink}>
        <SlicedText limit={40} text={name} />
      </Link>
    </CaptionedCell>
  );
};

const organizationConstraintName = () => ({
  header: (
    <TextWithDataTestId dataTestId="lbl_name">
      <FormattedMessage id="name" />
    </TextWithDataTestId>
  ),
  accessorKey: "name",
  cell: ({
    row: {
      original: { id, type, last_run: lastRun, limit_hits: limitHits = [] }
    },
    cell
  }) => <NameCell lastRun={lastRun} limitHitsCount={limitHits.length} id={id} type={type} name={cell.getValue()} />,
  defaultSort: "asc"
});

export default organizationConstraintName;
