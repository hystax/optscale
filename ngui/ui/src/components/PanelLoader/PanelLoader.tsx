import Grid from "@mui/material/Grid";
import Skeleton from "@mui/material/Skeleton";
import useStyles from "./PanelLoader.styles";

const PanelLoader = () => {
  const { classes } = useStyles();

  return (
    <Grid container direction="column">
      <Grid item xs>
        <Skeleton height={60} />
      </Grid>
      <Grid item xs className={classes.secondRow}>
        <Skeleton height={60} />
      </Grid>
      <Grid item xs className={classes.thirdRow}>
        <Skeleton height={60} />
      </Grid>
    </Grid>
  );
};

export default PanelLoader;
