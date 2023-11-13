import { useMemo, useState } from "react";
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

const FROM_BUCKET_COLUMN_ID = "cross-duplicates-from";

const CrossDuplicatesTable = ({ colorsRange, buckets, matrix }) => {
  const { checkId } = useParams();

  const matrixHeaderBuckets = useMemo(() => Object.keys(matrix), [matrix]);

  const tableData = useMemo(
    () =>
      Object.entries(matrix).map(([fromBucketId, relations]) => [
        buckets[fromBucketId],
        ...Object.keys(relations).map((toBucketId, matrixColumnIndex) => ({
          fromBucket: buckets[fromBucketId],
          toBucket: buckets[toBucketId],
          crossBucketsStats: matrix[fromBucketId][toBucketId],
          matrixColumnIndex
        }))
      ]),
    [buckets, matrix]
  );

  const matrixData = tableData.map((rowDatum) => [...rowDatum.slice(1)]);

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

  const columns = useMemo(
    () => [
      {
        id: FROM_BUCKET_COLUMN_ID,
        header: "",
        enableSorting: false,
        accessorFn: (originalRow) => originalRow[0],
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
        cell: ({ cell }) => {
          const bucket = cell.getValue();

          return (
            <>
              <Box
                display="flex"
                sx={{
                  wordBreak: "break-word"
                }}
              >
                <strong>{bucket.name}</strong>
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
        onRowCellClick: (e, { cell }) => {
          const bucket = cell.getValue();

          openSideModal(BucketDuplicatesModal, {
            bucket
          });
        }
      },
      ...matrixHeaderBuckets.map((headerBucketId, columnIndex) => ({
        id: headerBucketId,
        accessorFn: (originalRow) => originalRow[columnIndex + 1],
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
        cell: ({ cell }) => {
          const { fromBucket, crossBucketsStats } = cell.getValue();

          if (fromBucket.monthly_cost === undefined) {
            return CELL_EMPTY_VALUE;
          }

          return <FormattedMoney value={crossBucketsStats.monthly_savings} type={FORMATTED_MONEY_TYPES.TINY} />;
        },
        onRowCellClick: (e, { cell }) => {
          const { fromBucket, toBucket, crossBucketsStats } = cell.getValue();

          openSideModal(SelectedBucketsInfoModal, {
            checkId,
            fromBucket,
            toBucket,
            crossBucketsStats
          });

          setSelectedBuckets({
            from: fromBucket.name,
            to: toBucket.name
          });
        }
      }))
    ],
    [matrixHeaderBuckets, openSideModal, checkId]
  );

  const getRowCellClassName = (context) => {
    if (context.column.id === FROM_BUCKET_COLUMN_ID) {
      const {
        row: { index: rowIndex }
      } = context;
      const isCellInRowSelected = selectedBuckets ? selectedBuckets.from === matrixHeaderBuckets[rowIndex] : false;

      const selectedCellClassName = isCellInRowSelected ? classes.selectedFromCellBorder : "";

      const activityHoverClassName = css({
        "&:hover": {
          backgroundColor: theme.palette.action.hover,
          cursor: "pointer"
        }
      });

      return cx(selectedCellClassName, activityHoverClassName);
    }

    const {
      cell,
      row: { index: rowIndex }
    } = context;

    const { fromBucket, toBucket, crossBucketsStats } = cell.getValue();

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

    const isCellSelected = (rowBucketId, columnBucketId) =>
      selectedBuckets.from === rowBucketId && selectedBuckets.to === columnBucketId;

    const selectedMatrixRowIndex = selectedBuckets
      ? matrixData.findIndex(
          (rowDatum) =>
            !!rowDatum.find(
              (cellBuckets) =>
                cellBuckets.fromBucket.name === selectedBuckets.from && cellBuckets.toBucket.name === selectedBuckets.to
            )
        )
      : -1;

    const selectedMatrixColumnIndex =
      selectedMatrixRowIndex !== -1
        ? matrixData[selectedMatrixRowIndex].findIndex(
            (columnDatum) =>
              columnDatum.fromBucket.name === selectedBuckets.from && columnDatum.toBucket.name === selectedBuckets.to
          )
        : -1;

    const borderClassName = selectedBuckets
      ? getSelectionBorderClassName({
          selectedCellIndexes: {
            row: selectedMatrixRowIndex,
            column: selectedMatrixColumnIndex
          },
          cellIndexes: {
            row: rowIndex,
            column: context.cell.getValue().matrixColumnIndex
          }
        })
      : {};

    const backgroundColor =
      fromBucket.monthly_cost === undefined
        ? theme.palette.info.light
        : getCellRangeColor(crossBucketsStats.monthly_savings, colorsRange);

    const colorClassName = css({
      backgroundColor:
        selectedBuckets && !isCellSelected(fromBucket.name, toBucket.name)
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
  };

  const getHeaderCellClassName = (context) => {
    if (context.column.id === FROM_BUCKET_COLUMN_ID) {
      return undefined;
    }

    const isCellInColumnSelected = selectedBuckets ? selectedBuckets.to === context.column.id : false;

    return isCellInColumnSelected ? classes.selectedToCellBorder : "";
  };

  return (
    <Table
      data={tableData}
      columns={columns}
      stickySettings={{
        stickyHeader: true,
        scrollWrapperDOMId: BASE_LAYOUT_CONTAINER_ID
      }}
      memoBodyCells
      getRowCellClassName={getRowCellClassName}
      getHeaderCellClassName={getHeaderCellClassName}
    />
  );
};

export default CrossDuplicatesTable;
