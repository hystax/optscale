import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()(() => ({
  masked: {
    // this depends on text-security npm package
    fontFamily: "text-security-disc"
  }
}));

export default useStyles;
