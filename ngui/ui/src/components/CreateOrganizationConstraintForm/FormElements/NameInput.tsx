import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import { NAME_MAX_SIZE } from "utils/constants";
import { notOnlyWhiteSpaces } from "utils/validation";
import { CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES } from "../constants";

const FIELD_NAME = CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.NAME;

const NameInput = () => {
  const {
    register,
    formState: { errors }
  } = useFormContext();

  const intl = useIntl();

  return (
    <Input
      label={<FormattedMessage id="name" />}
      required
      dataTestId={`input_${FIELD_NAME}`}
      error={!!errors[FIELD_NAME]}
      helperText={errors[FIELD_NAME]?.message}
      {...register(FIELD_NAME, {
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        },
        maxLength: {
          value: NAME_MAX_SIZE,
          message: intl.formatMessage(
            { id: "maxLength" },
            { inputName: intl.formatMessage({ id: "value" }), max: NAME_MAX_SIZE }
          )
        },
        validate: {
          notOnlyWhiteSpaces
        }
      })}
    />
  );
};

export default NameInput;
