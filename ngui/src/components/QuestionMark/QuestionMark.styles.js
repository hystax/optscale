import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  questionMark: {
    cursor: "default",
    color: `${theme.palette.secondary.main} !important`,
    "&:hover": {
      backgroundColor: "inherit"
    }
  },
  rightSide: {
    paddingRight: 0
  }
}));

export default useStyles;
