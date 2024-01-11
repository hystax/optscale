import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import { DEFAULT_MAX_TEXTAREA_LENGTH } from "utils/constants";

const MlModelCreateFormDescriptionField = ({ name }) => {
  const {
    register,
    formState: { errors }
  } = useFormContext();

  const intl = useIntl();

  return (
    <Input
      dataTestId="input_description"
      label={<FormattedMessage id="description" />}
      error={!!errors[name]}
      helperText={errors[name] && errors[name].message}
      minRows={6}
      maxRows={16}
      multiline
      placeholder={intl.formatMessage({ id: "markdownIsSupported" })}
      {...register(name, {
        maxLength: {
          value: DEFAULT_MAX_TEXTAREA_LENGTH,
          message: intl.formatMessage(
            { id: "maxLength" },
            { inputName: intl.formatMessage({ id: "description" }), max: DEFAULT_MAX_TEXTAREA_LENGTH }
          )
        }
      })}
    />
  );
};

export default MlModelCreateFormDescriptionField;
