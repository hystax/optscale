import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import { DEFAULT_MAX_INPUT_LENGTH } from "utils/constants";
import { notOnlyWhiteSpaces } from "utils/validation";

export const FIELD_NAME = "path";

type EditModelVersionPathFormPathFieldProps = {
  name?: string;
};

const EditModelVersionPathFormPathField = ({ name = FIELD_NAME }: EditModelVersionPathFormPathFieldProps) => {
  const {
    register,
    formState: { errors }
  } = useFormContext();

  const intl = useIntl();

  return (
    <Input
      autoFocus
      label={<FormattedMessage id="path" />}
      dataTestId={`input_${name}`}
      error={!!errors[name]}
      helperText={errors[name]?.message}
      {...register(name, {
        maxLength: {
          value: DEFAULT_MAX_INPUT_LENGTH,
          message: intl.formatMessage(
            { id: "maxLength" },
            { inputName: intl.formatMessage({ id: "path" }), max: DEFAULT_MAX_INPUT_LENGTH }
          )
        },
        validate: {
          notOnlyWhiteSpaces
        }
      })}
    />
  );
};

export default EditModelVersionPathFormPathField;
