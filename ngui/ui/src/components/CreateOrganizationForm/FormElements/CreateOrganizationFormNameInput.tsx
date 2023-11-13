import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import { DEFAULT_MAX_INPUT_LENGTH } from "utils/constants";

export const NAME = "name";

const CreateOrganizationFormNameInput = () => {
  const intl = useIntl();

  const {
    formState: { errors },
    register
  } = useFormContext();

  return (
    <Input
      required
      dataTestId="input_new_organization_name"
      error={!!errors[NAME]}
      helperText={errors[NAME] && errors[NAME].message}
      label={<FormattedMessage id="name" />}
      {...register(NAME, {
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

export default CreateOrganizationFormNameInput;
