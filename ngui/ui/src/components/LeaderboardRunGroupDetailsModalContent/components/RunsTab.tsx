import { useMemo } from "react";
import { Link, Stack, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import CaptionedCell from "components/CaptionedCell";
import DynamicFractionDigitsValue from "components/DynamicFractionDigitsValue";
import KeyValueLabel from "components/KeyValueLabel";
import SubTitle from "components/SubTitle";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useFormatIntervalTimeAgo } from "hooks/useFormatIntervalTimeAgo";
import { getMlModelRunUrl, getMlRunsetDetailsUrl } from "urls";
import { dataset } from "utils/columns";
import { SPACING_2 } from "utils/layouts";
import { formatRunFullName } from "utils/ml";

const RUNS_TABLE_ROWS_PER_PAGE = 10;

const RunsTable = ({ runGroupPrimaryMetric, runGroupSecondaryMetrics, runsData }) => {
  const tableData = useMemo(() => runsData, [runsData]);
  const formatIntervalTimeAgo = useFormatIntervalTimeAgo();

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
            original: { runset_name: runsetName = "" }
          } = row;

          return [runName, runsetName].some((str) => str.toLocaleLowerCase().includes(search));
        },
        sortingFn: "alphanumeric",
        cell: ({ cell, row: { original } }) => {
          const { application_id: taskId, id: runId, finish, runset_id: runsetId, runset_name: runsetName } = original;

          return (
            <CaptionedCell
              caption={[
                {
                  node: <Typography variant="caption">{formatIntervalTimeAgo(finish, 1)}</Typography>,
                  key: "timeAgo"
                },
                ...(runsetName
                  ? [
                      {
                        node: (
                          <KeyValueLabel
                            typographyProps={{
                              variant: "caption"
                            }}
                            messageId="runset"
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
              <Link to={getMlModelRunUrl(taskId, runId)} component={RouterLink}>
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
      ...[runGroupPrimaryMetric, ...runGroupSecondaryMetrics].map(({ key, name }) => ({
        header: <TextWithDataTestId dataTestId={`lbl_${key}`}>{name}</TextWithDataTestId>,
        id: key,
        accessorFn: (originalRow) => originalRow.data?.[key]?.value,
        cell: ({ cell }) => <DynamicFractionDigitsValue value={cell.getValue()} />
      }))
    ],
    [formatIntervalTimeAgo, runGroupPrimaryMetric, runGroupSecondaryMetrics]
  );

  return (
    <Table
      data={tableData}
      columns={columns}
      localization={{
        emptyMessageId: "noRuns"
      }}
      pageSize={RUNS_TABLE_ROWS_PER_PAGE}
      enablePaginationQueryParam={false}
    />
  );
};

const RunsSection = ({ titleMessageId, runGroupPrimaryMetric, runGroupSecondaryMetrics, runs, isLoading }) => (
  <>
    <SubTitle>
      <FormattedMessage id={titleMessageId} />
    </SubTitle>
    {isLoading ? (
      <TableLoader />
    ) : (
      <RunsTable
        runGroupPrimaryMetric={runGroupPrimaryMetric}
        runGroupSecondaryMetrics={runGroupSecondaryMetrics}
        runsData={runs}
      />
    )}
  </>
);

const RunsTab = ({ runGroupPrimaryMetric, runGroupSecondaryMetrics, qualifiedRuns, otherDatasetRuns, isLoading = false }) => (
  <Stack spacing={SPACING_2}>
    <div>
      <RunsSection
        titleMessageId="qualifiedRuns"
        runGroupPrimaryMetric={runGroupPrimaryMetric}
        runGroupSecondaryMetrics={runGroupSecondaryMetrics}
        runs={qualifiedRuns}
        isLoading={isLoading}
      />
    </div>
    <div>
      <RunsSection
        titleMessageId="runsOnOtherDatasets"
        runGroupPrimaryMetric={runGroupPrimaryMetric}
        runGroupSecondaryMetrics={runGroupSecondaryMetrics}
        runs={otherDatasetRuns}
        isLoading={isLoading}
      />
    </div>
  </Stack>
);

export default RunsTab;
