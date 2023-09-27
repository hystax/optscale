import React from "react";
import { useTheme } from "@mui/material/styles";
import TableLoader from "components/TableLoader";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { STATUS } from "../../utils";
import CrossDuplicatesTable from "../CrossDuplicatesTable";

const useColorsRange = (thresholds) => {
  const theme = useTheme();

  const { requiringAttention, critical } = thresholds;

  const getSuccessRange = (range) => ({
    range,
    color: theme.palette.success.light
  });
  const getWarningRange = (range) => ({
    range,
    color: theme.palette.warning.light
  });
  const getErrorRange = (range) => ({
    range,
    color: theme.palette.error.light
  });

  const greenRange = [0, requiringAttention];
  const yellowRange = [requiringAttention, critical];
  const redRange = [critical, Infinity];

  return [getSuccessRange(greenRange), getWarningRange(yellowRange), getErrorRange(redRange)];
};

const Table = ({ matrix, buckets, thresholds }) => {
  const colorsRange = useColorsRange(thresholds);

  const maxCost = Math.max(
    ...Object.values(matrix).map((val) => {
      const savingsArray = Object.values(val).map(({ monthly_savings: monthlySavings = 0 }) => monthlySavings);
      return isEmptyArray(savingsArray) ? 0 : Math.max(...savingsArray);
    })
  );

  return <CrossDuplicatesTable maxCost={maxCost} colorsRange={colorsRange} buckets={buckets} matrix={matrix} />;
};

const DuplicatesInspector = ({ buckets, matrix, status, thresholds, isLoading }) => {
  if (isLoading) {
    return <TableLoader />;
  }

  if (status !== STATUS.SUCCESS) {
    return null;
  }

  return <Table matrix={matrix} buckets={buckets} thresholds={thresholds} />;
};

export default DuplicatesInspector;
