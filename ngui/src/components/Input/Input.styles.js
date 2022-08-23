import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()(() => ({
  masked: {
    fontFamily: "text-security-disc",
    /* Use -webkit-text-security if the browser supports it */
    "-webkit-text-security": "disc"
  }
}));

export default useStyles;
