import { useMemo } from "react";
import { useTheme } from "@mui/material/styles";
import { usePartialTheme } from "@nivo/theming";
import { remToPx } from "utils/fonts";

export const useChartTheme = () => {
  const theme = useTheme();

  const muiThemeTextFontSize = theme.typography.caption.fontSize;

  const muiThemeTextFontSizePixelsNumber = muiThemeTextFontSize.toString().includes("rem")
    ? remToPx(parseFloat(muiThemeTextFontSize))
    : parseInt(muiThemeTextFontSize, 10);

  const chartTheme = useMemo(
    () => ({
      canvas: {
        text: {
          fontFamily: theme.typography.fontFamily,
          fontSize: `${muiThemeTextFontSizePixelsNumber}px`,
          font: `${muiThemeTextFontSizePixelsNumber}px ${theme.typography.fontFamily}`,
        },
        marker: {
          xOffset: 14,
          yOffset: 10,
          lineDash: [10, 10],
          lineWidth: 2,
          color: theme.palette.error.main,
          font: `${muiThemeTextFontSizePixelsNumber}px ${theme.typography.fontFamily}`,
        },
      },
      labels: {
        text: {
          fontSize: muiThemeTextFontSizePixelsNumber,
          fontFamily: theme.typography.fontFamily,
        },
      },
      legends: {
        text: {
          fontSize: muiThemeTextFontSizePixelsNumber,
          fontFamily: theme.typography.fontFamily,
        },
      },
      axis: {
        domain: {
          line: {
            stroke: "transparent",
            strokeWidth: 1,
          },
        },
        ticks: {
          line: {
            stroke: theme.palette.info.light,
            strokeWidth: 1,
          },
          text: {
            // Canvas implementation doesn't support rems, it expects unitless value
            fontSize: muiThemeTextFontSizePixelsNumber,
            fontFamily: theme.typography.fontFamily,
            fill: theme.palette.text.primary,
          },
        },
      },
      tooltip: {
        zIndex: theme.zIndex.tooltip,
      },
    }),
    [
      muiThemeTextFontSizePixelsNumber,
      theme.palette.error.main,
      theme.palette.info.light,
      theme.palette.text.primary,
      theme.typography.fontFamily,
      theme.zIndex.tooltip,
    ]
  );

  return usePartialTheme(chartTheme);
};
