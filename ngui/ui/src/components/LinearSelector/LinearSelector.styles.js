import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => {
  const gap = theme.spacing(1);
  const halfGap = theme.spacing(0.5);

  return {
    wrapper: {
      display: "inline-flex",
      alignItems: "center",
      flexWrap: "wrap",
      margin: `-${gap} -${halfGap} 0 -${halfGap}`,
      "& > *": {
        margin: `${gap} ${halfGap} 0 ${halfGap}`
      },
      minHeight: "40px"
    },
    checkboxMenuItem: {
      paddingLeft: theme.spacing(1)
    },
    labelIcon: {
      // the same styles as for Button component with endIcon
      fontSize: "18px"
    },
    label: {
      display: "inline-flex"
    }
  };
});

export default useStyles;
