import React from "react";
import { FormControl, FormControlLabel, Switch, Typography } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import InputLoader from "components/InputLoader";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.GROUP_BY_HYPERPARAMETERS_FIELD_NAME;

const GroupByHyperparametersSwitch = ({ isLoading }) => {
  const { control } = useFormContext();

  return isLoading ? (
    <InputLoader fullWidth />
  ) : (
    <FormControl fullWidth>
      <FormControlLabel
        control={
          <Controller
            name={FIELD_NAME}
            control={control}
            render={({ field: { onChange, value } }) => <Switch checked={value} onChange={(e) => onChange(e.target.checked)} />}
          />
        }
        label={
          <Typography>
            <FormattedMessage id="groupByHyperparameters" />
          </Typography>
        }
      />
    </FormControl>
  );
};

export default GroupByHyperparametersSwitch;
