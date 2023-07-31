import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  wrapper: {
    wordBreak: "break-word",
    display: "flex",
    alignItems: "center",
    "& .animatedCopyIcon": {
      opacity: 0,
      transform: `translate(${theme.spacing(-1)}, 0px)`,
      transition: "opacity 0.2s ease 0s, transform 0.2s ease 0s"
    },
    "&:hover .animatedCopyIcon": {
      opacity: 1,
      transform: "translate(0px, 0px)"
    }
  },
  copyWrapper: {
    display: "inline-flex",
    paddingLeft: theme.spacing(0.5),
    cursor: "pointer"
  },
  normalWhitespace: { whiteSpace: "normal" }
}));

export default useStyles;
