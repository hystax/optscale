import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import { DEFAULT_MAX_INPUT_LENGTH } from "utils/constants";

export const FIELD_NAME = "name";

const DataSourceNameField = () => {
  const intl = useIntl();
  const {
    register,
    formState: { errors }
  } = useFormContext();

  return (
    <Input
      required
      dataTestId="input_cloud_account_name"
      error={!!errors[FIELD_NAME]}
      helperText={errors[FIELD_NAME] && errors[FIELD_NAME].message}
      label={<FormattedMessage id="name" />}
      {...register(FIELD_NAME, {
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        },
        maxLength: {
          value: DEFAULT_MAX_INPUT_LENGTH,
          message: intl.formatMessage(
            { id: "maxLength" },
            { inputName: intl.formatMessage({ id: "name" }), max: DEFAULT_MAX_INPUT_LENGTH }
          )
        }
      })}
    />
  );
};

export default DataSourceNameField;
