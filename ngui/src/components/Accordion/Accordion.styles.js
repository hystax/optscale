import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  details: {
    display: "block"
  },
  summary: {
    flexDirection: "row-reverse",
    "&.MuiAccordionSummary-root": {
      "&.Mui-expanded": {
        "& svg": {
          color: theme.palette.secondary.contrastText
        },
        "& p": {
          color: theme.palette.secondary.contrastText
        },
        "& input": {
          color: theme.palette.secondary.contrastText
        }
      }
    }
  },
  inheritFlexDirection: {
    flexDirection: "inherit"
  },
  summaryPadding: {
    padding: "0 0.5rem 0 0.5rem"
  },
  disableExpandedSpacing: {
    "&.Mui-expanded": {
      margin: 0
    }
  },
  zeroSummaryMinHeight: {
    minHeight: "0"
  }
}));

export default useStyles;
