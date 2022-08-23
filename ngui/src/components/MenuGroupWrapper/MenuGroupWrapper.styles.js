import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  menu: {
    "& .MuiAccordionSummary-root": {
      backgroundColor: "unset",
      color: theme.palette.info.main,
      justifyContent: "flex-start",
      "& .MuiAccordionSummary-expandIconWrapper": {
        transform: "rotate(0deg)",
        color: theme.palette.info.main
      },
      "& .MuiAccordionSummary-expandIconWrapper.Mui-expanded": {
        transform: "rotate(-180deg)"
      },
      "& .MuiAccordionSummary-content": {
        flexGrow: 0
      }
    },
    "& .MuiAccordionDetails-root": {
      padding: 0
    }
  }
}));

export default useStyles;
