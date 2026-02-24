import { ReactNode } from "react";
import { FormControlProps } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import RadioGroupField from "components/RadioGroupField";

type RadioGroupProps = {
  name: string;
  labelMessageId?: string;
  radioButtons: { label: ReactNode; value: string; disabled?: boolean; dataTestId?: string; isLoading?: boolean }[];
  defaultValue?: string;
  margin?: FormControlProps["margin"];
  row?: boolean;
  fullWidth?: boolean;
};

const RadioGroup = ({
  name,
  labelMessageId,
  radioButtons,
  defaultValue,
  margin,
  row = false,
  fullWidth = false,
}: RadioGroupProps) => {
  const {
    control,
    formState: { errors },
  } = useFormContext();

  return (
    <Controller
      control={control}
      name={name}
      defaultValue={defaultValue}
      render={({ field }) => (
        <RadioGroupField
          fullWidth={fullWidth}
          margin={margin}
          radioGroupProps={{ ...field, row }}
          labelMessageId={labelMessageId}
          error={errors?.[name]}
          helperText={errors?.[name]?.message}
          radioButtons={radioButtons}
        />
      )}
    />
  );
};

export default RadioGroup;
