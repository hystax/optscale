import { useRef } from "react";
import Box from "@mui/material/Box";
import Skeleton from "@mui/material/Skeleton";
import { useTheme } from "@mui/material/styles";
import { useResizeObserver } from "hooks/useResizeObserver";

const PieChartLoader = ({ height = 30 }) => {
  const theme = useTheme();

  const wrapperHeight = theme.spacing(height);

  const ref = useRef();
  const { width: wrapperWidth = 0 } = useResizeObserver(ref);

  // width and height should have the same unit - a number representing pixels
  const pieDiameter = Math.min(wrapperWidth, parseFloat(wrapperHeight));

  return (
    <Box ref={ref} display="flex" alignItems="center" justifyContent="center" height={wrapperHeight}>
      <Skeleton variant="circular" width={pieDiameter} height={pieDiameter} />
    </Box>
  );
};

export default PieChartLoader;
