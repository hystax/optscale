import { Fragment } from "react";
import { Box, Typography } from "@mui/material";
import { Stack } from "@mui/system";
import { FormattedMessage } from "react-intl";
import ExpandableList from "components/ExpandableList";
import HtmlSymbol from "components/HtmlSymbol";
import KeyValueLabel from "components/KeyValueLabel";
import LabelChip from "components/LabelChip";
import QuestionMark from "components/QuestionMark";
import SlicedText from "components/SlicedText";
import SummaryList from "components/SummaryList";
import TableLoader from "components/TableLoader";
import { isEmpty as isEmptyArray, isLastItem } from "utils/arrays";
import { DATASET_NAME_LENGTH_LIMIT } from "utils/constants";
import { isEmpty as isEmptyObject } from "utils/objects";
import LeaderboardCandidatesTable from "./LeaderboardCandidatesTable";

const METRIC_NAME_LENGTH_LIMIT = 50;
const TAG_NAME_LENGTH_LIMIT = 50;

const Summary = ({
  groupingTags = [],
  groupByHyperparameters = false,
  primaryMetric = {},
  secondaryMetrics = [],
  isLoading = false
}) => (
  <SummaryList
    titleMessage={<FormattedMessage id="summary" />}
    items={[
      <KeyValueLabel
        key="tagsForGrouping"
        keyMessageId="tagsForGrouping"
        value={groupingTags.map((tag, index, array) => (
          <Fragment key={tag}>
            <SlicedText text={tag} limit={TAG_NAME_LENGTH_LIMIT} />
            {isLastItem(index, array.length) ? "" : ", "}
          </Fragment>
        ))}
      />,
      <KeyValueLabel
        key="groupByHyperparameters"
        keyMessageId="groupByHyperparameters"
        value={<FormattedMessage id={groupByHyperparameters ? "yes" : "no"} />}
      />,
      <KeyValueLabel
        key="primaryMetric"
        keyMessageId="primaryMetric"
        value={<SlicedText text={primaryMetric.name} limit={METRIC_NAME_LENGTH_LIMIT} />}
      />,
      <KeyValueLabel
        key="secondaryMetrics"
        keyMessageId="secondaryMetrics"
        value={
          isEmptyArray(secondaryMetrics)
            ? undefined
            : secondaryMetrics.map(({ name }, index, array) => (
                <Fragment key={name}>
                  <SlicedText text={name} limit={METRIC_NAME_LENGTH_LIMIT} />
                  {isLastItem(index, array.length) ? "" : ", "}
                </Fragment>
              ))
        }
      />
    ]}
    isLoading={isLoading}
  />
);

const QualificationProtocol = ({ qualificationProtocol = [], isLoading = false }) => (
  <SummaryList
    titleMessage={<FormattedMessage id="qualificationProtocol" />}
    items={
      isEmptyArray(qualificationProtocol) ? (
        <FormattedMessage id="noRestrictions" />
      ) : (
        qualificationProtocol.map(({ name, min, max }) => (
          <KeyValueLabel
            key={name}
            keyText={<SlicedText text={name} limit={METRIC_NAME_LENGTH_LIMIT} />}
            value={`min: ${min ?? "-"}, max: ${max ?? "-"}`}
          />
        ))
      )
    }
    isLoading={isLoading}
  />
);

const DatasetCoverageRules = ({ datasets = [], coverageRules = {}, isLoading = false }) => {
  const hasCoverageRules = !isEmptyObject(coverageRules);
  const hasDatasets = !isEmptyArray(datasets);

  const hasDatasetCoverageRules = hasCoverageRules || hasDatasets;

  return (
    <SummaryList
      titleMessage={<FormattedMessage id="datasetsCoverageRules" />}
      items={
        hasDatasetCoverageRules ? (
          <>
            {hasDatasets && (
              <Box mb={1} display="flex" columnGap="4px" rowGap="2px" flexWrap="wrap" alignItems="center">
                <Typography
                  noWrap
                  component="span"
                  sx={{
                    display: "flex",
                    alignItems: "center"
                  }}
                >
                  <FormattedMessage id="datasets" />
                  <QuestionMark
                    tooltipText={
                      <>
                        <FormattedMessage id="candidateMustCoverFollowingDatasets" />
                        <HtmlSymbol symbol="period" />
                      </>
                    }
                    withLeftMargin={false}
                    fontSize="small"
                  />
                  &#58;
                </Typography>
                <ExpandableList
                  items={datasets}
                  render={({ name: datasetName }, index, items) => (
                    <span
                      key={datasetName}
                      style={{
                        overflowWrap: "anywhere"
                      }}
                    >
                      <strong>
                        <SlicedText key={datasetName} limit={DATASET_NAME_LENGTH_LIMIT} text={datasetName} />
                      </strong>
                      {!isLastItem(index, items.length) && (
                        <>
                          <HtmlSymbol symbol="comma" />
                        </>
                      )}
                    </span>
                  )}
                  maxRows={5}
                />
              </Box>
            )}
            {hasCoverageRules && (
              <Box mb={1} display="flex" columnGap="4px" rowGap="4px" flexWrap="wrap" alignItems="center">
                <Typography
                  noWrap
                  component="span"
                  sx={{
                    display: "flex",
                    alignItems: "center"
                  }}
                >
                  <FormattedMessage id="labels" />
                  <QuestionMark
                    tooltipText={
                      <>
                        <FormattedMessage id="candidateMustCoverDatasetsWithLabels" />
                        <HtmlSymbol symbol="period" />
                      </>
                    }
                    withLeftMargin={false}
                    fontSize="small"
                  />
                  &#58;
                </Typography>
                <ExpandableList
                  items={Object.entries(coverageRules)}
                  render={([label, amount]) => (
                    <LabelChip key={`${label}: ${amount}`} label={`${label}: ${amount}`} colorizeBy={label} />
                  )}
                  maxRows={5}
                />
              </Box>
            )}
          </>
        ) : (
          <FormattedMessage id="noDatasetsCoverageRules" />
        )
      }
      isLoading={isLoading}
    />
  );
};

const LeaderboardDetails = ({ leaderboard, leaderboardCandidates, isLoadingProps = {} }) => {
  const { isGetLeaderboardLoading, isGetLeaderboardCandidatesLoading } = isLoadingProps;

  const {
    grouping_tags: groupingTags = [],
    group_by_hp: groupByHyperparameters = false,
    primary_metric: primaryMetric = {},
    other_metrics: secondaryMetrics = [],
    filters: qualificationProtocol = []
  } = leaderboard;

  return (
    <>
      <Stack overflow="auto" flexGrow={1} spacing={1}>
        <Box>
          <Box display="flex" flexWrap="wrap" rowGap={2} columnGap={16}>
            <Box>
              <Summary
                groupingTags={groupingTags}
                groupByHyperparameters={groupByHyperparameters}
                primaryMetric={primaryMetric}
                secondaryMetrics={secondaryMetrics}
                isLoading={isGetLeaderboardLoading}
              />
            </Box>
            <Box>
              <QualificationProtocol qualificationProtocol={qualificationProtocol} isLoading={isGetLeaderboardLoading} />
            </Box>
            <Box>
              <DatasetCoverageRules
                datasets={leaderboard.datasets}
                coverageRules={leaderboard.dataset_coverage_rules ?? {}}
                isLoading={isGetLeaderboardLoading}
              />
            </Box>
          </Box>
        </Box>
        <Box>
          {isGetLeaderboardLoading || isGetLeaderboardCandidatesLoading ? (
            <TableLoader />
          ) : (
            <LeaderboardCandidatesTable leaderboard={leaderboard} leaderboardCandidates={leaderboardCandidates} />
          )}
        </Box>
      </Stack>
    </>
  );
};

export default LeaderboardDetails;
