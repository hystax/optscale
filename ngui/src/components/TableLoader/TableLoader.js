import React from "react";
import Grid from "@mui/material/Grid";
import Skeleton from "@mui/material/Skeleton";
import PropTypes from "prop-types";
import useStyles from "./TableLoader.styles";

const TableLoader = ({ columnsCounter, showHeader }) => {
  const { classes } = useStyles();

  const TableLoaderColumns = (counter) =>
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
        {TableLoaderColumns(columnsCounter)}
      </Grid>
    </>
  );
};

TableLoader.propTypes = {
  columnsCounter: PropTypes.number.isRequired,
  showHeader: PropTypes.bool
};

export default TableLoader;
