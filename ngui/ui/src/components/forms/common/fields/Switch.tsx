import { ReactNode } from "react";
import { FormControl, FormControlLabel, Switch as MuiSwitch } from "@mui/material";
import { Box } from "@mui/system";
import { Controller, useFormContext } from "react-hook-form";

type ShareSwitchProps = {
  name: string;
  label: ReactNode;
  adornment?: ReactNode;
  sx?: Record<string, unknown>;
};

const Switch = ({ name, label, adornment, sx }: ShareSwitchProps) => {
  const { control } = useFormContext();

  return (
    <FormControl fullWidth sx={sx}>
      <FormControlLabel
        control={
          <Controller
            name={name}
            control={control}
            render={({ field: { onChange, value } }) => (
              <MuiSwitch checked={value} onChange={(e) => onChange(e.target.checked)} />
            )}
          />
        }
        label={
          <Box display="flex" alignItems="center">
            {label}
            {adornment}
          </Box>
        }
      />
    </FormControl>
  );
};

export default Switch;
