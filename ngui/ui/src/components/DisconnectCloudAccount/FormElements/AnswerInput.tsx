import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";

const DEFAULT_MAX_INPUT_LENGTH = 500;

export const FIELD_OTHER = "other";
export const FIELD_CAPABILITIES = "capabilities";

const AnswerInput = ({ name, labelMessageId }) => {
  const {
    register,
    formState: { errors }
  } = useFormContext();

  const intl = useIntl();

  const maxSymbolsText = intl.formatMessage(
    { id: "maxLength" },
    { inputName: intl.formatMessage({ id: "answer" }), max: DEFAULT_MAX_INPUT_LENGTH }
  );

  return (
    <Input
      label={<FormattedMessage id={labelMessageId} />}
      error={!!errors[name]}
      helperText={errors[name] && errors[name].message}
      placeholder={maxSymbolsText}
      {...register(name, {
        maxLength: {
          value: DEFAULT_MAX_INPUT_LENGTH,
          message: maxSymbolsText
        }
      })}
      rows={4}
      multiline
    />
  );
};

export default AnswerInput;
