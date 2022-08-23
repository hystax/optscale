import { useTheme } from "@mui/material/styles";
import { remToPx } from "utils/fonts";

export const useChartTheme = () => {
  const theme = useTheme();

  const themeTextFontSize = theme.typography.caption.fontSize;

  return {
    // https://nivo.rocks/guides/theming
    axis: {
      ticks: {
        line: {
          stroke: theme.palette.info.light,
          strokeWidth: 1
        },
        text: {
          // Canvas implementation doesn't support rems, it expects unitless value
          fontSize: themeTextFontSize.toString().includes("rem")
            ? remToPx(parseFloat(themeTextFontSize))
            : parseInt(themeTextFontSize, 10),
          fontFamily: theme.typography.fontFamily,
          fill: theme.palette.text.primary
        }
      }
    },
    tooltip: {
      zIndex: theme.zIndex.tooltip
    }
  };
};
