import React from "react";
import Grid from "@mui/material/Grid";
import { useTheme } from "@mui/material/styles";
import PropTypes from "prop-types";

const GridContainerWithNegativeMarginCompensation = ({ children, spacing = 0, ...gridProps }) => {
  const theme = useTheme();

  return (
    // div is necessary to correct this error - https://material-ui.com/components/grid/#negative-margin.
    <div style={{ padding: theme.spacing(spacing / 2) }}>
      <Grid {...gridProps} container spacing={spacing}>
        {children}
      </Grid>
    </div>
  );
};

GridContainerWithNegativeMarginCompensation.propTypes = {
  children: PropTypes.node.isRequired,
  spacing: PropTypes.number
};

export default GridContainerWithNegativeMarginCompensation;
