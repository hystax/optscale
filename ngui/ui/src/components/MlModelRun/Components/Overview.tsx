import { Grid, Stack } from "@mui/material";
import { FormattedMessage } from "react-intl";
import CollapsableTableCell from "components/CollapsableTableCell";
import FormattedDuration from "components/FormattedDuration";
import MlRunStatus from "components/MlRunStatus/MlRunStatus";
import RunGoals from "components/RunGoals/RunGoals";
import SubTitle from "components/SubTitle";
import SummaryGrid from "components/SummaryGrid";
import TypographyLoader from "components/TypographyLoader";
import ExecutionBreakdownContainer from "containers/ExecutionBreakdownContainer";
import { ML_RUN_STATUS, SUMMARY_VALUE_COMPONENT_TYPES } from "utils/constants";
import { SPACING_2 } from "utils/layouts";
import { isEmpty as isEmptyObject } from "utils/objects";

const LOADER_LINES = 5;

const Status = ({ cost, status, duration, isLoading }) => (
  <SummaryGrid
    summaryData={[
      {
        key: "status",
        valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.Custom,
        CustomValueComponent: MlRunStatus,
        valueComponentProps: { status, iconSize: "medium" },
        color: {
          [ML_RUN_STATUS.RUNNING]: "primary",
          [ML_RUN_STATUS.ABORTED]: "primary",
          [ML_RUN_STATUS.COMPLETED]: "success",
          [ML_RUN_STATUS.FAILED]: "error"
        }[status],
        captionMessageId: "status",
        renderCondition: () => status !== undefined,
        isLoading,
        dataTestIds: {
          cardTestId: "card_run_status"
        }
      },
      {
        key: "duration",
        valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.Custom,
        CustomValueComponent: FormattedDuration,
        valueComponentProps: {
          durationInSeconds: duration ?? 0
        },
        renderCondition: () => status !== ML_RUN_STATUS.FAILED,
        captionMessageId: "duration",
        isLoading,
        dataTestIds: {
          cardTestId: "card_run_duration"
        }
      },
      {
        key: "cost",
        valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
        valueComponentProps: {
          value: cost ?? 0
        },
        captionMessageId: "expenses",
        dataTestIds: {
          cardTestId: "card_expenses"
        },
        isLoading
      }
    ]}
  />
);

const Goals = ({ reachedGoals, isLoading }) => {
  if (isLoading) {
    return <TypographyLoader linesCount={LOADER_LINES} />;
  }

  return !reachedGoals || isEmptyObject(reachedGoals) ? <FormattedMessage id="noGoals" /> : <RunGoals goals={reachedGoals} />;
};

const Tags = ({ tags, isLoading }) => {
  if (isLoading) {
    return <TypographyLoader linesCount={LOADER_LINES} />;
  }
  return !tags || isEmptyObject(tags) ? <FormattedMessage id="noTags" /> : <CollapsableTableCell tags={tags} />;
};

const Overview = ({ status, duration, cost, reachedGoals = {}, tags, isLoading = false }) => (
  <Stack spacing={SPACING_2}>
    <div>
      <Status cost={cost} status={status} isLoading={isLoading} duration={duration} />
    </div>
    <div>
      <Grid container spacing={SPACING_2}>
        <Grid item xs={12} sm={4}>
          <SubTitle>
            <FormattedMessage id="goals" />
          </SubTitle>
          <Goals reachedGoals={reachedGoals} isLoading={isLoading} />
        </Grid>
        <Grid item xs={12} sm={4}>
          <SubTitle>
            <FormattedMessage id="tags" />
          </SubTitle>
          <Tags tags={tags} isLoading={isLoading} />
        </Grid>
      </Grid>
    </div>
    <div>
      <SubTitle>
        <FormattedMessage id="execution" />
      </SubTitle>
      <ExecutionBreakdownContainer reachedGoals={reachedGoals} />
    </div>
  </Stack>
);

export default Overview;
