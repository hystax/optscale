import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => {
  const gap = theme.spacing(1);
  return {
    wrapper: {
      display: "inline-flex",
      alignItems: "center",
      flexWrap: "wrap",
      margin: `-${gap} 0 0 -${gap}`,
      "& > *": {
        margin: `${gap} 0 0 ${gap}`
      }
    }
  };
});

export default useStyles;
