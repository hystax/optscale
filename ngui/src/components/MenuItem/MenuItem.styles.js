import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  icon: {
    minWidth: "2rem"
  },
  nested: {
    paddingLeft: theme.spacing(6)
  },
  menuLink: {
    width: "100%",
    display: "contents",
    color: "inherit",
    textDecoration: "none"
  },
  activeLink: {
    color: theme.palette.secondary.contrastText,
    "& .MuiListItemSecondaryAction-root": {
      "& svg": {
        color: theme.palette.secondary.contrastText
      },
      "& span": {
        color: theme.palette.secondary.contrastText
      },
      "& .MuiIconButton-root": {
        "&:hover": {
          backgroundColor: theme.palette.secondary.light,
          "& svg": {
            color: theme.palette.secondary.contrastText
          },
          "& span": {
            color: theme.palette.secondary.contrastText
          }
        }
      }
    },
    "& .listItem": {
      backgroundColor: theme.palette.action.selected,
      "& svg": {
        color: theme.palette.secondary.contrastText
      },
      "& span": {
        color: theme.palette.secondary.contrastText
      }
    }
  }
}));

export default useStyles;
