import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  dropZone: {
    minHeight: theme.spacing(7),
    backgroundColor: theme.palette.background.paper,
    "& > *": {
      "&.MuiGrid-root": {
        width: "inherit",
        margin: 0,
        justifyContent: "center",
        "& > *": {
          padding: 0,
          "& > svg": {
            marginRight: 0,
            height: theme.spacing(7)
          },
          "& > button": {
            height: theme.spacing(4),
            width: theme.spacing(4)
          }
        }
      }
    }
  },
  title: {
    fontFamily: theme.typography.fontFamily,
    fontSize: theme.typography.pxToRem(16)
  }
}));

export default useStyles;
