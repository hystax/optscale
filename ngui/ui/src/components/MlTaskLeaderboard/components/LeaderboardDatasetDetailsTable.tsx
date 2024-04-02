import { useMemo, useState } from "react";
import EmojiEventsIcon from "@mui/icons-material/EmojiEvents";
import { Box, Divider, Stack, Typography } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import { FormattedMessage } from "react-intl";
import { useParams } from "react-router-dom";
import { v4 as uuidv4 } from "uuid";
import { AGGREGATE_FUNCTION_MESSAGE_ID } from "components/AggregateFunctionFormattedMessage";
import CollapsableTableCell from "components/CollapsableTableCell";
import DynamicFractionDigitsValue from "components/DynamicFractionDigitsValue";
import ExpandableList from "components/ExpandableList";
import IconLabel from "components/IconLabel";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import { LeaderboardRunGroupDetailsModal } from "components/SideModalManager/SideModals";
import Table from "components/Table";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { getIntersection, isEmpty as isEmptyArray } from "utils/arrays";
import { SPACING_1 } from "utils/layouts";
import { isEmpty as isEmptyObject } from "utils/objects";
import { CELL_EMPTY_VALUE } from "utils/tables";

const RANKINGS = Object.freeze({
  TOP_ONE: 1,
  TOP_TWO: 2,
  TOP_THREE: 3
});

const RANKING_ICON_SIZE = "1.5rem";

const LeaderboardDatasetDetailsTable = ({ primaryMetric, leaderboardDataset, leaderboardDatasetDetails }) => {
  const theme = useTheme();
  const { taskId } = useParams();

  const [selectedRow, setSelectedRow] = useState();

  const openSideModal = useOpenSideModal();

  const RANKING_COLORS = useMemo(
    () => ({
      [RANKINGS.TOP_ONE]: theme.palette.gold.main,
      [RANKINGS.TOP_TWO]: theme.palette.silver.main,
      [RANKINGS.TOP_THREE]: theme.palette.bronze.main
    }),
    [theme.palette.bronze.main, theme.palette.gold.main, theme.palette.silver.main]
  );

  const runGroups = useMemo(
    () =>
      leaderboardDatasetDetails.map((datum, index) => ({
        ...datum,
        id: uuidv4(),
        /**
         * Backend guaranties that data is sorted by ranking in descending order
         * so we can use index to defined ui ranking
         */
        ranking:
          getIntersection(datum.qualification, leaderboardDataset.dataset_ids).length === leaderboardDataset.dataset_ids.length
            ? index + 1
            : undefined,
        coverage: {
          covered: datum.qualification.length,
          all: leaderboardDataset.dataset_ids.length
        }
      })),
    [leaderboardDataset.dataset_ids, leaderboardDatasetDetails]
  );

  const qualifiedTableData = useMemo(() => runGroups.filter(({ ranking }) => !!ranking), [runGroups]);

  const notQualifiedTableData = useMemo(() => runGroups.filter(({ ranking }) => !ranking), [runGroups]);

  const columns = useMemo(
    () => [
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_ranking">
            <FormattedMessage id="ranking" />
          </TextWithDataTestId>
        ),
        accessorKey: "ranking",
        emptyValue: " ",
        enableSorting: false,
        style: {
          width: "80px"
        },
        cell: ({ cell }) => {
          const ranking = cell.getValue();

          if (ranking > RANKINGS.TOP_THREE) {
            return ranking;
          }

          return (
            <IconLabel
              label={
                <>
                  {ranking}
                  &nbsp;
                </>
              }
              endIcon={
                <EmojiEventsIcon
                  style={{
                    color: RANKING_COLORS[ranking],
                    fontSize: RANKING_ICON_SIZE
                  }}
                />
              }
            />
          );
        }
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_coverage">
            <FormattedMessage id="coverage" />
          </TextWithDataTestId>
        ),
        id: "coverage",
        enableSorting: false,
        style: {
          width: "150px"
        },
        cell: ({
          row: {
            original: { coverage: { covered, all } = {} }
          }
        }) => (
          <FormattedMessage
            id="value / value"
            values={{
              value1: covered,
              value2: all
            }}
          />
        )
      },
      {
        header: (
          <Box>
            <TextWithDataTestId dataTestId={`lbl_metric_${primaryMetric.key}`}>{primaryMetric.name}</TextWithDataTestId>
            <Typography>
              {AGGREGATE_FUNCTION_MESSAGE_ID[primaryMetric.func] ? (
                <FormattedMessage id={AGGREGATE_FUNCTION_MESSAGE_ID[primaryMetric.func]} />
              ) : (
                primaryMetric.func
              )}
            </Typography>
          </Box>
        ),
        id: "primaryMetricScore",
        enableSorting: false,
        accessorFn: (originalRow) => originalRow.primary_metric?.[primaryMetric.key]?.value,
        style: {
          width: "150px"
        },
        cell: ({ cell }) => <DynamicFractionDigitsValue value={cell.getValue()} />
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_secondary_metrics">
            <FormattedMessage id="secondaryMetrics" />
          </TextWithDataTestId>
        ),
        id: "secondaryMetrics",
        enableSorting: false,
        style: {
          width: "200px"
        },
        cell: ({
          row: {
            original: { metrics = {} }
          }
        }) =>
          isEmptyObject(metrics) ? (
            CELL_EMPTY_VALUE
          ) : (
            <ExpandableList
              items={Object.values(metrics).sort(({ name: nameA }, { name: nameB }) => nameA.localeCompare(nameB))}
              render={({ name, value }) => (
                <KeyValueLabel
                  key={name}
                  keyText={name}
                  value={value === null ? undefined : <DynamicFractionDigitsValue value={value} />}
                />
              )}
              maxRows={5}
            />
          )
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_tags">
            <FormattedMessage id="tags" />
          </TextWithDataTestId>
        ),
        id: "tags",
        enableSorting: false,
        style: {
          width: "500px"
        },
        cell: ({
          row: {
            original: { tags = {} }
          }
        }) => (isEmptyObject(tags) ? CELL_EMPTY_VALUE : <CollapsableTableCell maxRows={5} tags={tags} />)
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_hyperparameters">
            <FormattedMessage id="hyperparameters" />
          </TextWithDataTestId>
        ),
        id: "hyperparameters",
        enableSorting: false,
        style: {
          width: "500px"
        },
        cell: ({
          row: {
            original: { hyperparams = {} }
          }
        }) =>
          isEmptyObject(hyperparams) ? (
            CELL_EMPTY_VALUE
          ) : (
            <CollapsableTableCell
              maxRows={5}
              tags={Object.fromEntries(Object.entries(hyperparams).filter(([, value]) => value !== null))}
            />
          )
      }
    ],
    [primaryMetric.key, primaryMetric.name, primaryMetric.func, RANKING_COLORS]
  );

  return (
    <Stack spacing={SPACING_1} overflow="auto">
      <div>
        <Table
          data={qualifiedTableData}
          columns={columns}
          onRowClick={(row) => {
            setSelectedRow(row);
            openSideModal(LeaderboardRunGroupDetailsModal, {
              groupDetails: row,
              leaderboardDataset,
              taskId
            });
          }}
          localization={{
            emptyMessageId: "noQualifiedGroups"
          }}
          tableLayout="fixed"
          isSelectedRow={(row) => !!selectedRow && row.id === selectedRow.id}
          overflowX="initial"
          disableBottomBorderForLastRow
        />
      </div>
      {!isEmptyArray(notQualifiedTableData) && (
        <>
          <Box position="sticky" p={1} left={0}>
            <Box
              position="absolute"
              top="-2px"
              left="50%"
              width="90px"
              textAlign="center"
              sx={{
                backgroundColor: () => theme.palette.background.paper,
                left: "calc(50% - 45px)"
              }}
            >
              <FormattedMessage id="qualification" />
            </Box>
            <Divider
              sx={{
                borderStyle: "dashed"
              }}
            />
          </Box>
          <div>
            <Table
              withHeader={false}
              data={notQualifiedTableData}
              columns={columns}
              onRowClick={(row) => {
                setSelectedRow(row);
                openSideModal(LeaderboardRunGroupDetailsModal, {
                  groupDetails: row,
                  leaderboardDataset,
                  taskId
                });
              }}
              tableLayout="fixed"
              isSelectedRow={(row) => !!selectedRow && row.id === selectedRow.id}
              overflowX="initial"
            />
          </div>
        </>
      )}
    </Stack>
  );
};

export default LeaderboardDatasetDetailsTable;
