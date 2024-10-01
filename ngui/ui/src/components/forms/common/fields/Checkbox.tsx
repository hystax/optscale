import { ReactNode } from "react";
import { Box } from "@mui/material";
import MuiCheckbox from "@mui/material/Checkbox";
import FormControlLabel from "@mui/material/FormControlLabel";
import { useFormContext, Controller } from "react-hook-form";
import CheckboxLoader from "components/CheckboxLoader";

type CheckboxProps = {
  name: string;
  label: ReactNode;
  defaultValue?: boolean;
  adornment?: ReactNode;
  disabled?: boolean;
  isLoading?: boolean;
};

const Checkbox = ({ name, label, defaultValue, adornment, disabled = false, isLoading = false }: CheckboxProps) => {
  const { control } = useFormContext();

  return isLoading ? (
    <CheckboxLoader fullWidth />
  ) : (
    <FormControlLabel
      control={
        <Controller
          name={name}
          control={control}
          defaultValue={defaultValue}
          render={({ field: { value, onChange, ...rest } }) => (
            <MuiCheckbox
              data-test-id={`${name}-checkbox`}
              checked={value ?? false}
              disabled={disabled}
              {...rest}
              onChange={(event) => onChange(event.target.checked)}
            />
          )}
        />
      }
      label={
        <Box data-test-id={`${name}-checkbox-label`} display="flex" alignItems="center">
          {label}
          {adornment}
        </Box>
      }
    />
  );
};

export default Checkbox;
