import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  mono: {
    ...theme.typography.mono
  }
}));

export default useStyles;
