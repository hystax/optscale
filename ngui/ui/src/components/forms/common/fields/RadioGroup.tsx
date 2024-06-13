import { ReactNode } from "react";
import { Controller, useFormContext } from "react-hook-form";
import RadioGroupField from "components/RadioGroupField";

type RadioGroupProps = {
  name: string;
  labelMessageId?: string;
  radioButtons: { label: ReactNode; value: string; disabled?: boolean; dataTestId?: string }[];
};

const RadioGroup = ({ name, labelMessageId, radioButtons }: RadioGroupProps) => {
  const {
    control,
    formState: { errors }
  } = useFormContext();

  return (
    <Controller
      control={control}
      name={name}
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
