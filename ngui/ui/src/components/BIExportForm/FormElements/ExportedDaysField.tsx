import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import InputLoader from "components/InputLoader";
import QuestionMark from "components/QuestionMark";
import { MAX_INT_32 } from "utils/constants";
import { isWholeNumber } from "utils/validation";

export const FIELD_NAME = "budget";

const ExportedDaysField = ({ isLoading }) => {
  const {
    register,
    formState: { errors }
  } = useFormContext();

  const intl = useIntl();

  return isLoading ? (
    <InputLoader fullWidth />
  ) : (
    <Input
      dataTestId="input_exported_days"
      label={<FormattedMessage id="exportedDays" />}
      required
      error={!!errors[FIELD_NAME]}
      InputProps={{
        endAdornment: <QuestionMark messageId="exportedDaysDescription" dataTestId="qmark_exported_days" />
      }}
      helperText={errors[FIELD_NAME] && errors[FIELD_NAME].message}
      {...register(FIELD_NAME, {
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        },
        min: {
          value: 0,
          message: intl.formatMessage({ id: "moreOrEqual" }, { min: 0 })
        },
        max: {
          value: MAX_INT_32,
          message: intl.formatMessage({ id: "lessOrEqual" }, { max: MAX_INT_32 })
        },
        validate: {
          whole: (value) => (isWholeNumber(value) ? intl.formatMessage({ id: "wholeNumber" }) : true)
        }
      })}
    />
  );
};

export default ExportedDaysField;
