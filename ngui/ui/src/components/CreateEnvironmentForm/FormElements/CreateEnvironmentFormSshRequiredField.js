import React from "react";
import Checkbox from "@mui/material/Checkbox";
import FormControlLabel from "@mui/material/FormControlLabel";
import { useFormContext, Controller } from "react-hook-form";
import { FormattedMessage } from "react-intl";

const NAME = "requireSshKey";

const CreateEnvironmentFormSshRequiredField = () => {
  const { control } = useFormContext();

  return (
    <FormControlLabel
      control={
        <Controller
          name={NAME}
          control={control}
          render={({ field: { value, onChange, ...rest } }) => (
            <Checkbox
              data-test-id="checkbox_ssh_only"
              checked={value ?? false}
              {...rest}
              onChange={(event) => onChange(event.target.checked)}
            />
          )}
        />
      }
      label={
        <span data-test-id="ssh_only_label">
          <FormattedMessage id="requireSshKey" />
        </span>
      }
    />
  );
};

export default CreateEnvironmentFormSshRequiredField;
