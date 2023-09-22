import React, { useMemo, useState } from "react";
import { Box } from "@mui/material";
import { lighten, useTheme } from "@mui/material/styles";
import { useParams } from "react-router-dom";
import FormattedMoney from "components/FormattedMoney";
import KeyValueLabel from "components/KeyValueLabel";
import QuestionMark from "components/QuestionMark";
import { BucketDuplicatesModal, SelectedBucketsInfoModal } from "components/SideModalManager/SideModals";
import Table from "components/Table";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { BASE_LAYOUT_CONTAINER_ID, FORMATTED_MONEY_TYPES } from "utils/constants";
import { isEmpty as isEmptyObject } from "utils/objects";
import { CELL_EMPTY_VALUE } from "utils/tables";
import useStyles from "./CrossDuplicatesTable.styles";

const getCellRangeColor = (number, colorsRange) => {
  const { color } = colorsRange.find(({ range }) => number <= range[1] && number >= range[0]);

  return color;
};

const CrossDuplicatesTable = ({ colorsRange, buckets, matrix }) => {
  const { checkId } = useParams();

  const matrixHeaderBuckets = Object.keys(matrix);

  const matrixCellBuckets = Object.entries(matrix).map(([fromBucketId, relations]) =>
    Object.keys(relations).map((toBucketId) => [fromBucketId, toBucketId])
  );

  const [selectedBuckets, setSelectedBuckets] = useState(() => {
    // Matrix is sorted by monthly cost so we can check only the 1st row if it has a monthly cost value
    if (!isEmptyObject(buckets) && buckets[matrixHeaderBuckets[0]].monthly_cost !== undefined) {
      return {
        from: matrixHeaderBuckets[0],
        to: matrixHeaderBuckets[0]
      };
    }

    return null;
  });

  const { css, cx, classes } = useStyles();
  const theme = useTheme();

  const openSideModal = useOpenSideModal();

  const columns = useMemo(() => {
    const isCellSelected = (rowBucketId, columnBucketId) =>
      selectedBuckets.from === rowBucketId && selectedBuckets.to === columnBucketId;

    const getSelectionBorderClassName = ({ selectedCellIndexes, cellIndexes }) => {
      const { row: selectedCellRowIndex, column: selectedCellColumnIndex } = selectedCellIndexes;

      const { row: cellRowIndex, column: cellColumnIndex } = cellIndexes;

      if (selectedCellRowIndex === cellRowIndex && selectedCellColumnIndex === cellColumnIndex) {
        return classes.selectedCellBorders;
      }

      if (selectedCellColumnIndex === cellColumnIndex && cellRowIndex < selectedCellRowIndex) {
        return classes.cellInColumnPathBorders;
      }

      if (cellRowIndex === selectedCellRowIndex && selectedCellColumnIndex > cellColumnIndex) {
        return classes.cellInRowPathBorders;
      }

      return {};
    };

    return [
      {
        id: "cross-duplicates-from",
        header: "",
        enableSorting: false,
        headerStyle: {
          /*
            Make sure header cell in the 1st column covers rest columns and rows when scrolling
          */
          zIndex: 1
        },
        style: {
          minWidth: "250px",
          height: "65px",
          backgroundColor: "white",
          position: "sticky",
          left: 0
        },
        getRowCellClassName: ({ row: { index: rowIndex } }) => {
          const isCellInRowSelected = selectedBuckets ? selectedBuckets.from === matrixHeaderBuckets[rowIndex] : false;

          const selectedCellClassName = isCellInRowSelected ? classes.selectedFromCellBorder : "";

          const activityHoverClassName = css({
            "&:hover": {
              backgroundColor: theme.palette.action.hover,
              cursor: "pointer"
            }
          });

          return cx(selectedCellClassName, activityHoverClassName);
        },
        cell: ({ row: { index: rowIndex } }) => {
          const bucketId = matrixHeaderBuckets[rowIndex];
          const bucket = buckets[bucketId];

          return (
            <>
              <Box
                display="flex"
                sx={{
                  wordBreak: "break-word"
                }}
              >
                <strong>{bucketId}</strong>
                {bucket.monthly_cost === undefined && (
                  <QuestionMark messageId="expensesForThisBucketHaveNotBeenDiscoveredYet" />
                )}
              </Box>
              <KeyValueLabel
                messageId="possibleMonthlySavings"
                flexWrap="nowrap"
                value={bucket.monthly_savings === undefined ? "-" : <FormattedMoney value={bucket.monthly_savings} />}
                type={FORMATTED_MONEY_TYPES.TINY}
              />
            </>
          );
        },
        onRowCellClick: (e, { row: { index: rowIndex } }) => {
          const bucketId = matrixHeaderBuckets[rowIndex];
          const bucket = buckets[bucketId];

          openSideModal(BucketDuplicatesModal, {
            bucket
          });
        }
      },
      ...matrixCellBuckets.map((datum, columnIndex) => {
        const headerBucketId = matrixHeaderBuckets[columnIndex];

        return {
          id: `cross-duplicates-to-${headerBucketId}`,
          header: (
            <strong
              style={{
                wordBreak: "break-word"
              }}
            >
              {headerBucketId}
            </strong>
          ),
          headerStyle: {
            minWidth: "220px"
          },
          getHeaderCellClassName: () => {
            const isCellInColumnSelected = selectedBuckets ? selectedBuckets.to === headerBucketId : false;

            return isCellInColumnSelected ? classes.selectedToCellBorder : "";
          },
          getRowCellClassName: ({ row: { index: rowIndex } }) => {
            const [fromBucketId, toBucketId] = matrixCellBuckets[rowIndex][columnIndex];
            const fromBucket = buckets[fromBucketId];

            const selectedRowIndex = selectedBuckets
              ? matrixCellBuckets.findIndex(
                  (rowDatum) =>
                    !!rowDatum.find(
                      (cellBuckets) => cellBuckets[0] === selectedBuckets.from && cellBuckets[1] === selectedBuckets.to
                    )
                )
              : -1;

            const selectedColumnIndex =
              selectedRowIndex !== -1
                ? matrixCellBuckets[selectedRowIndex].findIndex(
                    (columnDatum) => columnDatum[0] === selectedBuckets.from && columnDatum[1] === selectedBuckets.to
                  )
                : -1;

            const borderClassName = selectedBuckets
              ? getSelectionBorderClassName({
                  selectedCellIndexes: {
                    row: selectedRowIndex,
                    column: selectedColumnIndex
                  },
                  cellIndexes: {
                    row: rowIndex,
                    column: columnIndex
                  }
                })
              : {};

            const backgroundColor =
              fromBucket.monthly_cost === undefined
                ? theme.palette.info.light
                : getCellRangeColor(matrix[fromBucketId][toBucketId].monthly_savings, colorsRange);

            const colorClassName = css({
              backgroundColor:
                selectedBuckets && !isCellSelected(fromBucketId, toBucketId)
                  ? lighten(backgroundColor, 0.8)
                  : lighten(backgroundColor, 0.7)
            });

            const activityHoverClassName = css({
              "&:hover": {
                backgroundColor: lighten(backgroundColor, 0.65),
                cursor: "pointer"
              }
            });

            return cx([colorClassName, borderClassName, activityHoverClassName]);
          },
          cell: ({ row: { index: rowIndex } }) => {
            const [fromBucketId, toBucketId] = matrixCellBuckets[rowIndex][columnIndex];

            const fromBucket = buckets[fromBucketId];

            if (fromBucket.monthly_cost === undefined) {
              return CELL_EMPTY_VALUE;
            }

            return (
              <FormattedMoney value={matrix[fromBucketId][toBucketId].monthly_savings} type={FORMATTED_MONEY_TYPES.TINY} />
            );
          },
          onRowCellClick: (e, { row: { index: rowIndex } }) => {
            const [fromBucketId, toBucketId] = matrixCellBuckets[rowIndex][columnIndex];

            openSideModal(SelectedBucketsInfoModal, {
              checkId,
              fromBucket: buckets[fromBucketId],
              toBucket: buckets[toBucketId],
              crossBucketsStats: matrix[fromBucketId][toBucketId]
            });

            setSelectedBuckets({
              from: fromBucketId,
              to: toBucketId
            });
          }
        };
      })
    ];
  }, [
    matrixCellBuckets,
    selectedBuckets,
    classes.selectedCellBorders,
    classes.cellInColumnPathBorders,
    classes.cellInRowPathBorders,
    classes.selectedFromCellBorder,
    classes.selectedToCellBorder,
    matrixHeaderBuckets,
    theme,
    css,
    cx,
    buckets,
    matrix,
    colorsRange,
    openSideModal,
    checkId
  ]);

  return (
    <Table
      data={matrixCellBuckets}
      columns={columns}
      stickySettings={{
        stickyHeader: true,
        scrollWrapperDOMId: BASE_LAYOUT_CONTAINER_ID
      }}
    />
  );
};

export default CrossDuplicatesTable;
