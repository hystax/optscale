import { useCallback, useMemo } from "react";
import { Link, Stack, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import CaptionedCell from "components/CaptionedCell";
import { useFormatDynamicFractionDigitsValue } from "components/DynamicFractionDigitsValue";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import SubTitle from "components/SubTitle";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useFormatIntervalTimeAgo } from "hooks/useFormatIntervalTimeAgo";
import { getMlTaskRunUrl, getMlRunsetDetailsUrl } from "urls";
import { dataset } from "utils/columns";
import { SPACING_2 } from "utils/layouts";
import { formatRunFullName } from "utils/ml";

const RUNS_TABLE_ROWS_PER_PAGE = 10;

const useFormatRunTimeAgo = () => {
  const formatIntervalTimeAgo = useFormatIntervalTimeAgo();

  return useCallback((finish) => formatIntervalTimeAgo(finish, 1), [formatIntervalTimeAgo]);
};

const RunsTable = ({ candidatePrimaryMetric, candidateSecondaryMetrics, runsData }) => {
  const tableData = useMemo(() => runsData, [runsData]);

  const formatRunTimeAgo = useFormatRunTimeAgo();
  const formatDynamicFractionDigitsValue = useFormatDynamicFractionDigitsValue();

  const columns = useMemo(
    () => [
      {
        header: <TextWithDataTestId dataTestId="lbl_#">#</TextWithDataTestId>,
        id: "runName",
        accessorFn: ({ number, name }) => formatRunFullName(number, name),
        defaultSort: "desc",
        style: {
          width: "200px"
        },
        searchFn: (runName, filterValue, { row }) => {
          const search = filterValue.toLocaleLowerCase();

          const {
            original: { runset_name: runsetName, finish }
          } = row;

          const timeAgo = formatRunTimeAgo(finish);

          return [
            runName,
            timeAgo,
            // runsetName can be null
            runsetName ?? ""
          ].some((str) => str.toLocaleLowerCase().includes(search));
        },
        sortingFn: "alphanumeric",
        cell: ({ cell, row: { original } }) => {
          const { task_id: taskId, id: runId, finish, runset_id: runsetId, runset_name: runsetName } = original;

          return (
            <CaptionedCell
              caption={[
                {
                  node: <Typography variant="caption">{formatRunTimeAgo(finish)}</Typography>,
                  key: "timeAgo"
                },
                ...(runsetName
                  ? [
                      {
                        node: (
                          <KeyValueLabel
                            variant="caption"
                            keyMessageId="runset"
                            value={
                              <Link to={getMlRunsetDetailsUrl(runsetId)} component={RouterLink}>
                                {runsetName}
                              </Link>
                            }
                          />
                        ),
                        key: "template"
                      }
                    ]
                  : [])
              ]}
            >
              <Link to={getMlTaskRunUrl(taskId, runId)} component={RouterLink}>
                {cell.getValue()}
              </Link>
            </CaptionedCell>
          );
        }
      },
      dataset({
        id: "dataset",
        accessorFn: (originalRow) => originalRow.dataset?.name
      }),
      ...[candidatePrimaryMetric, ...candidateSecondaryMetrics].map(({ key, name }) => ({
        header: <TextWithDataTestId dataTestId={`lbl_${key}`}>{name}</TextWithDataTestId>,
        id: key,
        searchFn: (value, filterValue) => {
          const search = filterValue.toLocaleLowerCase();

          return formatDynamicFractionDigitsValue({ value }).includes(search);
        },
        accessorFn: (originalRow) => originalRow.data?.[key]?.value,
        cell: ({ cell }) => formatDynamicFractionDigitsValue({ value: cell.getValue() })
      }))
    ],
    [formatDynamicFractionDigitsValue, formatRunTimeAgo, candidatePrimaryMetric, candidateSecondaryMetrics]
  );

  return (
    <Table
      data={tableData}
      columns={columns}
      localization={{
        emptyMessageId: "noRuns"
      }}
      withSearch
      pageSize={RUNS_TABLE_ROWS_PER_PAGE}
      enablePaginationQueryParam={false}
      enableSearchQueryParam={false}
    />
  );
};

const RunsSection = ({ titleMessageId, candidatePrimaryMetric, candidateSecondaryMetrics, runs, isLoading }) => (
  <>
    <SubTitle>
      <FormattedMessage id={titleMessageId} />
    </SubTitle>
    {isLoading ? (
      <TableLoader />
    ) : (
      <RunsTable
        candidatePrimaryMetric={candidatePrimaryMetric}
        candidateSecondaryMetrics={candidateSecondaryMetrics}
        runsData={runs}
      />
    )}
  </>
);

const RunsTab = ({ candidatePrimaryMetric, candidateSecondaryMetrics, qualifiedRuns, otherDatasetRuns, isLoading = false }) => (
  <Stack spacing={SPACING_2}>
    <div>
      <RunsSection
        titleMessageId="qualifiedRuns"
        candidatePrimaryMetric={candidatePrimaryMetric}
        candidateSecondaryMetrics={candidateSecondaryMetrics}
        runs={qualifiedRuns}
        isLoading={isLoading}
      />
    </div>
    <div>
      <RunsSection
        titleMessageId="runsOnOtherDatasets"
        candidatePrimaryMetric={candidatePrimaryMetric}
        candidateSecondaryMetrics={candidateSecondaryMetrics}
        runs={otherDatasetRuns}
        isLoading={isLoading}
      />
    </div>
  </Stack>
);

export default RunsTab;
