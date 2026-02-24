import { makeStyles } from "tss-react/mui";

const getExpandColorStyles = ({ theme, expandTitleColor, alwaysHighlightTitle = false }) => {
  const style = {
    background: {
      backgroundColor: theme.palette.background.default,
    },
  }[expandTitleColor] ?? {
    color: theme.palette.secondary.contrastText,
    backgroundColor: theme.palette.action.selected,
    "& svg": {
      color: theme.palette.secondary.contrastText,
    },
    "& p": {
      color: theme.palette.secondary.contrastText,
    },
    "& input": {
      color: theme.palette.secondary.contrastText,
    },
  };

  return {
    "&.MuiAccordionSummary-root": alwaysHighlightTitle
      ? style
      : {
          "&.Mui-expanded": style,
        },
  };
};

const useStyles = makeStyles()((theme, { expandTitleColor, alwaysHighlightTitle }) => ({
  details: {
    display: "block",
  },
  summary: {
    flexDirection: "row-reverse",
  },
  enableBorder: {
    borderBottom: `1px solid ${theme.palette.divider}`,
  },
  disableShadows: {
    boxShadow: "none",
  },
  inheritFlexDirection: {
    flexDirection: "inherit",
  },
  summaryPadding: {
    padding: "0 0.5rem 0 0.5rem",
  },
  disableExpandedSpacing: {
    "&.Mui-expanded": {
      margin: 0,
    },
  },
  zeroSummaryMinHeight: {
    minHeight: "0",
  },
  expandTitleColor: getExpandColorStyles({ theme, expandTitleColor, alwaysHighlightTitle }),
}));

export default useStyles;
