import React from "react";
import { Typography } from "@mui/material";
import PropTypes from "prop-types";
import useStyles from "./TableContent.styles";

const TableContent = ({ data }) => {
  // TODO: Handle 0 items count
  const columnsCount = data[0]?.length ?? 0;
  const { classes } = useStyles(columnsCount);
  return (
    <Typography component="div" className={classes.grid}>
      {data.flat().map(({ key, value }) => (
        <div key={key}>{value}</div>
      ))}
    </Typography>
  );
};

TableContent.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.arrayOf(PropTypes.shape({ key: PropTypes.any.isRequired, value: PropTypes.any.isRequired }))
  )
};

export default TableContent;
