import Grid from "@mui/material/Grid";
import Skeleton from "@mui/material/Skeleton";
import useStyles from "./TableLoader.styles";

type TableLoaderProps = {
  showHeader?: boolean;
  columnsCounter?: number;
};

const TableLoader = ({ showHeader, columnsCounter = 3 }: TableLoaderProps) => {
  const { classes } = useStyles();

  const renderTableLoaderColumns = (counter: number) =>
    [...Array(counter).keys()].map((x) => (
      <Grid key={`column-${x}`} item xs>
        <Grid container direction="column">
          <Grid item xs>
            <Skeleton height={40} />
          </Grid>
          <Grid item xs className={classes.secondRow}>
            <Skeleton height={40} />
          </Grid>
          <Grid item xs className={classes.thirdRow}>
            <Skeleton height={40} />
          </Grid>
        </Grid>
      </Grid>
    ));

  return (
    <>
      {showHeader ? <Skeleton height={60} /> : null}
      <Grid container direction="row" spacing={3}>
        {renderTableLoaderColumns(columnsCounter)}
      </Grid>
    </>
  );
};

export default TableLoader;
