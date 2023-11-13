import { alpha } from "@mui/material/styles";
import { makeStyles } from "tss-react/mui";
import { SPACING_1 } from "utils/layouts";

const useStyles = makeStyles()((theme) => ({
  selector: {
    marginRight: theme.spacing(SPACING_1),
    "&:last-child": {
      marginRight: 0
    }
  },
  selectRoot: {
    "& svg": {
      color: theme.palette.info.main
    }
  },
  notSelectedItem: {
    "& svg": {
      color: theme.palette.info.main
    }
  },
  menuTitle: {
    fontWeight: "bold",
    pointerEvents: "none"
  },
  menuItem: {
    paddingLeft: theme.spacing(4)
  },
  sectionDesktopXs: {
    display: "none",
    [theme.breakpoints.up("xs")]: {
      display: "inline-flex"
    }
  },
  sectionMobileXs: {
    display: "flex",
    [theme.breakpoints.up("xs")]: {
      display: "none"
    }
  },
  sectionDesktopSm: {
    display: "none",
    [theme.breakpoints.up("sm")]: {
      display: "inline-flex"
    }
  },
  sectionMobileSm: {
    display: "flex",
    [theme.breakpoints.up("sm")]: {
      display: "none"
    }
  },
  sectionDesktopMd: {
    display: "none",
    [theme.breakpoints.up("md")]: {
      display: "inline-flex"
    }
  },
  sectionMobileMd: {
    display: "flex",
    [theme.breakpoints.up("md")]: {
      display: "none"
    }
  },
  sectionDesktopLg: {
    display: "none",
    [theme.breakpoints.up("lg")]: {
      display: "inline-flex"
    }
  },
  sectionMobileLg: {
    display: "flex",
    [theme.breakpoints.up("lg")]: {
      display: "none"
    }
  },
  button: {
    color: theme.palette.primary.main,
    "&:hover": {
      backgroundColor: alpha(theme.palette.primary.main, 0.2)
    }
  },
  mobileSelect: {
    visibility: "hidden",
    maxWidth: 0
  },
  iconPositionWithAdornment: {
    // W/o positioning expand arrow overlaps with adornment
    position: "relative"
  }
}));

export default useStyles;
