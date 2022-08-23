import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  name: {
    display: "inline-block"
  },
  avatarWrapper: {
    minWidth: "0"
  },
  avatar: {
    backgroundColor: "transparent",
    width: "max-content"
  },
  avatarItem: {
    fontSize: "2rem",
    paddingRight: "0.5rem"
  },
  redAvatarItem: {
    color: theme.palette.error.main
  },
  greenAvatarItem: {
    color: theme.palette.success.main
  },
  yellowAvatarItem: {
    color: theme.palette.warning.main
  },
  listItem: {
    paddingTop: "0",
    paddingBottom: "0"
  },
  text: {
    color: theme.palette.text.primary,
    display: "inline"
  }
}));

export default useStyles;
