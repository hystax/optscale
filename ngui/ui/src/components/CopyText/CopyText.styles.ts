import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  wrapper: {
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
  }
}));

export default useStyles;
