import React from "react";
import Skeleton from "@mui/material/Skeleton";
import { useTheme } from "@mui/material/styles";
import PropTypes from "prop-types";
import { DEFAULT_BAR_CHART_HEIGHT } from "utils/constants";

const BarChartLoader = ({ height = DEFAULT_BAR_CHART_HEIGHT, width = "100%" }) => {
  const theme = useTheme();
  return <Skeleton variant="rectangular" height={theme.spacing(height)} width={width} />;
};

BarChartLoader.propTypes = {
  height: PropTypes.number,
  width: PropTypes.oneOfType([PropTypes.string, PropTypes.number])
};

export default BarChartLoader;
