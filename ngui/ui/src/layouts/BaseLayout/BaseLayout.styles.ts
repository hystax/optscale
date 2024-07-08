import { makeStyles } from "tss-react/mui";
import { SPACING_1 } from "utils/layouts";

export const DRAWER_WIDTH = 205;

const useStyles = makeStyles()((theme) => ({
  appBar: {
    boxShadow: "none"
  },
  toolbar: {
    display: "flex",
    height: theme.spacing(7),
    justifyContent: "space-between",
    backgroundColor: theme.palette.info.header
  },
  logo: {
    [theme.breakpoints.down("md")]: {
      flex: 1
    }
  },
  marginRight1: {
    marginRight: theme.spacing(SPACING_1)
  },
  marginLeft1: {
    marginLeft: theme.spacing(SPACING_1)
  },
  drawerPaper: {
    position: "relative",
    width: DRAWER_WIDTH
  },
  content: {
    overflowY: "auto",
    paddingLeft: "0",
    paddingRight: "0",
    maxWidth: "none",
    // that way PageContentWrapper will fill whole page height
    display: "flex",
    flexDirection: "column"
  },
  mobileRegisterButton: {
    backgroundColor: theme.palette.success.main,
    color: "inherit"
  },
  layoutWrapper: {
    display: "flex",
    flexDirection: "column",
    height: "100vh"
  },
  menuAndContentWrapper: {
    overflow: "hidden",
    flexGrow: 1,
    display: "flex"
  },
  wrapper: {
    overflow: "hidden",
    display: "grid",
    gridTemplateColumns: "minmax(0, 1fr) 0",
    [theme.breakpoints.up("md")]: {
      transition: "grid-template-columns 0.2s ease-in"
    }
  },
  wrapperWithDocsOpened: {
    [theme.breakpoints.up("md")]: {
      gridTemplateColumns: `minmax(0, 1fr) 400px`
    },
    gridTemplateColumns: `0 minmax(0, 1fr)`
  },
  hideableLayoutWrapper: {
    [theme.breakpoints.down("md")]: {
      visibility: "hidden"
    }
  }
}));

export default useStyles;
