import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import InputLoader from "components/InputLoader";
import { DEFAULT_MAX_INPUT_LENGTH } from "utils/constants";
import { notOnlyWhiteSpaces } from "utils/validation";

export const FIELD_NAME = "s3Prefix";

const S3PrefixField = ({ isLoading }) => {
  const {
    register,
    formState: { errors }
  } = useFormContext();

  const intl = useIntl();

  return isLoading ? (
    <InputLoader fullWidth />
  ) : (
    <Input
      dataTestId="input_s3_prefix"
      key={FIELD_NAME}
      error={!!errors[FIELD_NAME]}
      helperText={errors[FIELD_NAME] && errors[FIELD_NAME].message}
      label={<FormattedMessage id="s3Prefix" />}
      {...register(FIELD_NAME, {
        maxLength: {
          value: DEFAULT_MAX_INPUT_LENGTH,
          message: intl.formatMessage(
            { id: "maxLength" },
            { inputName: intl.formatMessage({ id: "s3Prefix" }), max: DEFAULT_MAX_INPUT_LENGTH }
          )
        },
        validate: {
          notOnlyWhiteSpaces
        }
      })}
    />
  );
};

export default S3PrefixField;
