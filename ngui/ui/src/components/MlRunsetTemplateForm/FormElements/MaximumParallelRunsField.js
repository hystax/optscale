import React from "react";
import { Switch } from "@mui/material";
import FormControlLabel from "@mui/material/FormControlLabel";
import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import Tooltip from "components/Tooltip";

const MaximumParallelRunsField = () => (
  <Tooltip title={<FormattedMessage id="comingSoon" />}>
    <FormControlLabel
      control={<Switch disabled checked={false} />}
      label={
        <Typography>
          <FormattedMessage id="limitMaximumParallelRunsNumber" />
        </Typography>
      }
      labelPlacement="end"
    />
  </Tooltip>
);

export default MaximumParallelRunsField;
