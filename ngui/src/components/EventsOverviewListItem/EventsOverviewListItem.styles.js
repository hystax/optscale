import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  listItem: {
    padding: "0"
  },
  warning: {
    backgroundColor: theme.palette.warning.main
  },
  error: {
    backgroundColor: theme.palette.error.main
  },
  success: {
    backgroundColor: theme.palette.success.main
  },
  info: {
    backgroundColor: theme.palette.info.main
  },
  level: {
    width: ".5rem",
    minHeight: "100%"
  },
  title: {
    fontWeight: "bold"
  },
  timeAgo: {
    fontWeight: "bold"
  },
  description: {
    wordBreak: "break-word"
  }
}));

export default useStyles;
