import React from "react";
import { Box, FormControl, InputLabel, MenuItem, OutlinedInput, Select } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import { makeStyles } from "tss-react/mui";
import Checkbox from "components/Checkbox";
import Chip from "components/Chip";
import CloudLabel from "components/CloudLabel";
import { useIsNebiusConnectionEnabled } from "hooks/useIsNebiusConnectionEnabled";
import { AWS_CNR, AZURE_CNR, NEBIUS } from "utils/constants";

export const FIELD_NAME = "cloudProvider";

const useStyles = makeStyles()((theme) => ({
  // overriding theme style — no need for selected items background in this control
  menuItem: {
    "&.Mui-selected": {
      backgroundColor: "unset",
      "&.Mui-focusVisible": { background: "unset" },
      "&:hover": {
        backgroundColor: "unset"
      }
    }
  },
  checkbox: {
    padding: `0 ${theme.spacing(1)} 0 0`
  }
}));

export const SUPPORTED_CLOUD_TYPES = [
  { name: "aws", type: AWS_CNR },
  {
    name: "azure",
    type: AZURE_CNR
  },
  {
    name: "nebius",
    type: NEBIUS
  }
];

const CloudProviderField = () => {
  const { classes } = useStyles();
  const intl = useIntl();

  const {
    control,
    formState: { errors }
  } = useFormContext();

  const isNebiusConnectionEnabled = useIsNebiusConnectionEnabled();

  const items = SUPPORTED_CLOUD_TYPES.filter(({ type }) => {
    if (type === NEBIUS && !isNebiusConnectionEnabled) {
      return false;
    }
    return true;
  }).map(({ name, type }) => ({
    name: intl.formatMessage({ id: name }),
    type
  }));

  return (
    <Controller
      name={FIELD_NAME}
      control={control}
      render={({ field: { value, onChange, ref, ...restControllerFieldProps } }) => (
        <FormControl fullWidth>
          <InputLabel required shrink id="cloud-provider-label">
            <FormattedMessage id="cloudProvider" />
          </InputLabel>
          <Select
            onChange={(e) => {
              onChange(e.target.value);
            }}
            multiple
            value={value}
            error={!!errors[FIELD_NAME]}
            inputRef={ref}
            labelId="cloud-provider-label"
            input={<OutlinedInput notched required label={<FormattedMessage id="cloudProvider" />} />}
            displayEmpty
            renderValue={(selected) => {
              if (selected.length === 0) {
                return <FormattedMessage id="all" />;
              }
              const selectedDataSourcesChips = items
                .map(({ name, type }) => {
                  if (selected.includes(type)) {
                    return (
                      <Chip
                        key={type}
                        size="small"
                        label={<CloudLabel name={name} type={type} disableLink />}
                        variant="outlined"
                        stopMouseDownPropagationOnDelete
                        onDelete={() => onChange(value.filter((val) => val !== type))}
                      />
                    );
                  }
                  return false;
                })
                .filter(Boolean);

              return <Box>{selectedDataSourcesChips}</Box>;
            }}
            {...restControllerFieldProps}
          >
            {items.map(({ name, type }) => (
              <MenuItem key={type} value={type} className={classes.menuItem}>
                <Checkbox checked={value.includes(type)} className={classes.checkbox} />
                <CloudLabel name={name} type={type} disableLink />
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      )}
    />
  );
};

export default CloudProviderField;
