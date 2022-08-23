import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  button: {
    textTransform: "none",
    fontSize: "1rem",
    "&:hover": {
      backgroundColor: "white"
    },
    marginRight: theme.spacing(1)
  },
  icon: {
    marginRight: theme.spacing(0.5)
  },
  uppercase: {
    textTransform: "uppercase"
  },
  rtl: {
    marginRight: 0,
    marginLeft: theme.spacing(1)
  },
  link: {
    textDecoration: "none",
    color: "inherit"
  },
  tooltipSpan: {
    display: "block" // Required for disabled items in Safari (https://material-ui.com/components/tooltips/#disabled-elements).
  },
  childItem: {
    paddingLeft: theme.spacing(1)
  }
}));

export default useStyles;
