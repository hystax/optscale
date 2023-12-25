import { Controller, useFormContext } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import RadioGroupField from "components/RadioGroupField";
import { FIELD_NAMES, SAVE_AS_VALUES } from "../constants";

const SaveAsRadioGroup = ({ name = FIELD_NAMES.SAVE_AS, saveThisDisabled = false }) => {
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
          error={!!errors?.[name]}
          helperText={errors?.[name]?.message}
          radioButtons={[
            {
              dataTestId: "radio_btn_save_this",
              disabled: saveThisDisabled,
              value: SAVE_AS_VALUES.SAVE_THIS,
              label: <FormattedMessage id="saveThisDashboard" />
            },
            {
              dataTestId: "radio_btn_save_as_new",
              value: SAVE_AS_VALUES.SAVE_AS_NEW,
              label: <FormattedMessage id="saveAsNewDashboard" />
            }
          ]}
        />
      )}
    />
  );
};

export default SaveAsRadioGroup;
