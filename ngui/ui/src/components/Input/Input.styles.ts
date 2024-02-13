import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()(() => ({
  masked: {
    // this depends on text-security npm package
    fontFamily: "text-security-disc",
    // use -webkit-text-security if the browser supports it
    WebkitTextSecurity: "disc"
  }
}));

export default useStyles;
