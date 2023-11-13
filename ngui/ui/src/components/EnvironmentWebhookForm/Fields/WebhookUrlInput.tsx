import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import { DEFAULT_MAX_INPUT_LENGTH } from "utils/constants";

const WebhookUrlInput = ({ name }) => {
  const intl = useIntl();
  const {
    register,
    formState: { errors }
  } = useFormContext();

  return (
    <Input
      margin="none"
      required
      error={!!errors[name]}
      helperText={errors[name]?.message}
      label={<FormattedMessage id="url" />}
      {...register(name, {
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        },
        maxLength: {
          value: DEFAULT_MAX_INPUT_LENGTH,
          message: intl.formatMessage(
            { id: "maxLength" },
            {
              inputName: intl.formatMessage({ id: "url" }),
              max: DEFAULT_MAX_INPUT_LENGTH
            }
          )
        }
      })}
    />
  );
};

export default WebhookUrlInput;
