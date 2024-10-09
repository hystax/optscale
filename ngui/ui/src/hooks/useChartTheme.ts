import { useMemo } from "react";
import { useTheme } from "@mui/material/styles";
import { remToPx } from "utils/fonts";

export const useChartTheme = () => {
  const theme = useTheme();

  const themeTextFontSize = theme.typography.caption.fontSize;

  const themTextFontSizePixelsNumber = themeTextFontSize.toString().includes("rem")
    ? remToPx(parseFloat(themeTextFontSize))
    : parseInt(themeTextFontSize, 10);

  // https://nivo.rocks/guides/theming
  return useMemo(
    () => ({
      canvas: {
        text: {
          fontFamily: theme.typography.fontFamily,
          fontSize: `${themTextFontSizePixelsNumber}px`,
          font: `${themTextFontSizePixelsNumber}px ${theme.typography.fontFamily}`
        },
        marker: {
          xOffset: 14,
          yOffset: 10,
          lineDash: [10, 10],
          lineWidth: 2,
          color: theme.palette.error.main,
          font: `${themTextFontSizePixelsNumber}px ${theme.typography.fontFamily}`
        }
      },
      labels: {
        text: {
          fontSize: themTextFontSizePixelsNumber,
          fontFamily: theme.typography.fontFamily
        }
      },
      axis: {
        domain: {
          line: {
            stroke: "transparent",
            strokeWidth: 1
          }
        },
        ticks: {
          line: {
            stroke: theme.palette.info.light,
            strokeWidth: 1
          },
          text: {
            // Canvas implementation doesn't support rems, it expects unitless value
            fontSize: themTextFontSizePixelsNumber,
            fontFamily: theme.typography.fontFamily,
            fill: theme.palette.text.primary
          }
        }
      },
      tooltip: {
        zIndex: theme.zIndex.tooltip
      }
    }),
    [
      themTextFontSizePixelsNumber,
      theme.palette.error.main,
      theme.palette.info.light,
      theme.palette.text.primary,
      theme.typography.fontFamily,
      theme.zIndex.tooltip
    ]
  );
};
