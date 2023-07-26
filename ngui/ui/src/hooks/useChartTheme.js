import { useMemo } from "react";
import { useTheme } from "@mui/material/styles";
import { remToPx } from "utils/fonts";

export const useChartTheme = () => {
  const theme = useTheme();

  const themeTextFontSize = theme.typography.caption.fontSize;

  const themTextFontSizePixelsNumber = themeTextFontSize.toString().includes("rem")
    ? remToPx(parseFloat(themeTextFontSize))
    : parseInt(themeTextFontSize, 10);

  return useMemo(
    () => ({
      canvas: {
        text: {
          fontFamily: theme.typography.fontFamily,
          fontSize: `${themTextFontSizePixelsNumber}px`,
          font: `${themTextFontSizePixelsNumber}px ${theme.typography.fontFamily}`
        }
      },
      // https://nivo.rocks/guides/theming
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
      theme.palette.info.light,
      theme.palette.text.primary,
      theme.typography.fontFamily,
      theme.zIndex.tooltip
    ]
  );
};
