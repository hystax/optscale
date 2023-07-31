import React from "react";
import Grid from "@mui/material/Grid";
import PropTypes from "prop-types";
import { SPACING_1 } from "utils/layouts";

const PropertyGridLayout = ({ propertyName, propertyValue, iconButtons }) => (
  <Grid container spacing={SPACING_1}>
    <Grid item xs={12} sm={4} md={5} lg={4}>
      {propertyName}
    </Grid>
    <Grid item xs={12} sm={8} md={7} lg={8}>
      <div style={{ display: "flex" }}>
        <div style={{ width: "100%", marginRight: "16px", overflow: "auto" }}>{propertyValue}</div>
        {iconButtons && (
          <div style={{ width: "fit-content", display: "inline-flex", height: "fit-content", justifyContent: "flex-end" }}>
            {iconButtons}
          </div>
        )}
      </div>
    </Grid>
  </Grid>
);

PropertyGridLayout.propTypes = {
  propertyName: PropTypes.node.isRequired,
  propertyValue: PropTypes.node.isRequired,
  iconButtons: PropTypes.node
};

export default PropertyGridLayout;
