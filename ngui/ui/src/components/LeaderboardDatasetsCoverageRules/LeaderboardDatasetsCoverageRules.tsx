import CheckCircleOutlinedIcon from "@mui/icons-material/CheckCircleOutlined";
import WarningAmberOutlinedIcon from "@mui/icons-material/WarningAmberOutlined";
import { Stack, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import ExpandableList from "components/ExpandableList";
import IconLabel from "components/IconLabel";
import LabelChip from "components/LabelChip";
import { isEmpty as isEmptyArray } from "utils/arrays";

type NoDatasetsCoverageRulesMessageProps = {
  message?: {
    text?: string;
    messageId?: string;
  };
};

type LeaderboardDatasetsCoverageRulesProps = {
  datasets: {
    all: number;
    covered: number;
  };
  coverageRules: {
    label: string;
    covered: number;
    all: number;
  }[];
  noDatasetsCoverageRulesMessage?: NoDatasetsCoverageRulesMessageProps["message"];
};

type CoverageStatusProps = {
  covered: number;
  all: number;
};

const CoverageStatus = ({ covered, all }: CoverageStatusProps) => (
  <IconLabel
    icon={
      covered === all ? (
        <CheckCircleOutlinedIcon fontSize="inherit" color="success" />
      ) : (
        <WarningAmberOutlinedIcon fontSize="inherit" color="error" />
      )
    }
    label={
      <Typography fontWeight="bold" whiteSpace="nowrap">
        <FormattedMessage
          id="value / value"
          values={{
            value1: covered,
            value2: all
          }}
        />
      </Typography>
    }
  />
);

const NoDatasetsCoverageRulesMessage = ({ message = {} }: NoDatasetsCoverageRulesMessageProps) => {
  const { text, messageId = "noDatasetsCoverageRules" } = message;

  return <Typography>{text ?? <FormattedMessage id={messageId} />}</Typography>;
};

const LeaderboardDatasetsCoverageRules = ({
  datasets,
  coverageRules,
  noDatasetsCoverageRulesMessage
}: LeaderboardDatasetsCoverageRulesProps) => {
  const hasDatasetsCovered = datasets.all > 0;
  const hasCoverageRules = !isEmptyArray(coverageRules);
  const hasDatasetsCoverageRules = hasDatasetsCovered || hasCoverageRules;

  return hasDatasetsCoverageRules ? (
    <Stack spacing={0.5}>
      {hasDatasetsCovered && (
        <Typography component="div" display="flex" alignItems="center">
          <FormattedMessage id="datasets" />
          :&nbsp;
          <CoverageStatus covered={datasets.covered} all={datasets.all} />
        </Typography>
      )}
      {hasCoverageRules && (
        <ExpandableList
          items={coverageRules}
          render={({ label, covered, all }) => (
            <Typography key={label} component="div" display="flex" alignItems="center">
              <LabelChip label={label} colorizeBy={label} labelSymbolsLimit={20} />
              :&nbsp;
              <CoverageStatus covered={covered} all={all} />
            </Typography>
          )}
          maxRows={4}
          stopPropagationOnShowMore
        />
      )}
    </Stack>
  ) : (
    <NoDatasetsCoverageRulesMessage message={noDatasetsCoverageRulesMessage} />
  );
};

export default LeaderboardDatasetsCoverageRules;
