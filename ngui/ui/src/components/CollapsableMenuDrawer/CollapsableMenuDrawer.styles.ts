import { lighten } from "@mui/material";
import { makeStyles } from "tss-react/mui";
import { DRAWER_WIDTH } from "layouts/BaseLayout/BaseLayout.styles";
import { SPACING_2 } from "utils/layouts";

const INTERACTIVE_BORDER_WIDTH = 20;

const ANIMATION_LENGTH = 0.2;

const ANIMATION_FUNCTION = "ease-out";

const useStyles = makeStyles()((theme, { buttonOpacity, isExpanded }) => ({
  // wrapper does not have width in collapsed form (interactive border width stays)
  // this way even when menu is opened on hover, page content is not moving/resizing
  wrapper: {
    display: "flex",
    flexDirection: "row",
    transition: `width ${ANIMATION_LENGTH}s ${ANIMATION_FUNCTION}`,
    width: `${INTERACTIVE_BORDER_WIDTH}px`
  },
  wrapperExpanded: {
    width: `${DRAWER_WIDTH}px`
  },
  // hiding menu using its margin
  menu: {
    width: DRAWER_WIDTH,
    transition: `margin ${ANIMATION_LENGTH}s ${ANIMATION_FUNCTION}`,
    marginLeft: 0,
    height: "100%"
  },
  hiddenMenu: {
    marginLeft: `${-DRAWER_WIDTH + INTERACTIVE_BORDER_WIDTH}px`
  },
  menuCollapseBorder: {
    right: `${INTERACTIVE_BORDER_WIDTH / 2}px`,
    zIndex: theme.zIndex.drawer,
    cursor: "pointer",
    position: "relative",
    minWidth: `${INTERACTIVE_BORDER_WIDTH}px`
  },
  drawerPaper: {
    position: "relative",
    paddingRight: 0,
    background: "white",
    "& > *": {
      // opacity of drawer children helps to move away currently selected menu item background, when menu is collapsed
      opacity: 1,
      transition: `opacity ${ANIMATION_LENGTH / 2}s ${ANIMATION_FUNCTION} 0s`
    }
  },
  drawerPaperHidden: {
    "& > *": {
      opacity: 0,
      transition: `opacity ${ANIMATION_LENGTH}s ${ANIMATION_FUNCTION} ${ANIMATION_LENGTH / 2}s`
    },
    scrollbarWidth: "none",
    "::-webkit-scrollbar": {
      display: "none"
    }
  },
  button: {
    position: "absolute",
    borderColor: lighten(theme.palette.info.main, 0.8),
    borderWidth: "1px",
    borderStyle: "solid",
    backgroundColor: theme.palette.common.white,
    color: theme.palette.info.main,
    padding: "0.25rem",
    transform: "translateX(-50%)",
    left: "50%",
    top: theme.spacing(SPACING_2),
    borderRadius: "50%",
    transition: "opacity 0.2s ease-in",
    opacity: buttonOpacity,
    ":hover": {
      backgroundColor: theme.palette.primary.main,
      color: theme.palette.common.white
    }
  },
  buttonIcon: {
    transition: "transform 0.2s ease-in",
    transform: `rotate(${isExpanded ? "180" : "0"}deg) scale(0.8)`,
    fontSize: "inherit"
  }
}));

export default useStyles;
