import React from "react";
import { Typography } from "@mui/material";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { COST_MODEL_TYPES } from "utils/constants";
import useStyles from "./UpdateCostModelWarning.styles";

const UpdateCostModelWarning = ({ costModelType, dataTestId }) => {
  const { classes } = useStyles();
  return (
    <Typography className={classes.warningText} gutterBottom data-test-id={dataTestId}>
      <FormattedMessage
        id="costModelFormWarning"
        values={{
          break: <br />,
          costModelType
        }}
      />
    </Typography>
  );
};

UpdateCostModelWarning.propTypes = {
  costModelType: PropTypes.oneOf(Object.values(COST_MODEL_TYPES)),
  dataTestId: PropTypes.string
};

export default UpdateCostModelWarning;
