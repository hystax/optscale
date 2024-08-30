import { ReactNode } from "react";
import { Controller, useFormContext } from "react-hook-form";
import RadioGroupField from "components/RadioGroupField";

type RadioGroupProps = {
  name: string;
  labelMessageId?: string;
  radioButtons: { label: ReactNode; value: string; disabled?: boolean; dataTestId?: string }[];
  defaultValue?: string;
};

const RadioGroup = ({ name, labelMessageId, radioButtons, defaultValue }: RadioGroupProps) => {
  const {
    control,
    formState: { errors }
  } = useFormContext();

  return (
    <Controller
      control={control}
      name={name}
      defaultValue={defaultValue}
      render={({ field }) => (
        <RadioGroupField
          fullWidth
          radioGroupProps={field}
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
