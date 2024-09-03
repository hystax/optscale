import { ReactNode } from "react";
import { useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import Input from "components/Input";
import InputLoader from "components/InputLoader";
import { DEFAULT_MAX_INPUT_LENGTH } from "utils/constants";
import { idx } from "utils/objects";
import { notOnlyWhiteSpaces } from "utils/validation";

type TextInputProps = {
  name: string;
  label?: ReactNode;
  required?: boolean;
  autoFocus?: boolean;
  dataTestId?: string;
  isLoading?: boolean;
  InputProps?: Record<string, unknown>;
  inputProps?: Record<string, unknown>;
  maxLength?: number | null;
  minLength?: number | null;
  validate?: Record<string, unknown>;
  placeholder?: string;
  rows?: number;
  multiline?: boolean;
  type?: string;
  autoComplete?: string;
  margin?: "none" | "dense" | "normal";
  pattern?: {
    value: RegExp;
    message: string;
  };
  sx?: Record<string, unknown>;
  minRows?: number;
  maxRows?: number;
  disabled?: boolean;
  defaultValue?: string;
  masked?: boolean;
  className?: string;
  fullWidth?: boolean;
  shouldUnregister?: boolean;
};

const TextInput = ({
  name,
  label,
  required = false,
  autoFocus = false,
  dataTestId,
  isLoading = false,
  InputProps,
  inputProps,
  maxLength = DEFAULT_MAX_INPUT_LENGTH,
  minLength = null,
  validate,
  placeholder,
  rows,
  multiline,
  type,
  autoComplete,
  margin,
  pattern,
  sx,
  minRows,
  maxRows,
  disabled,
  defaultValue,
  masked,
  className,
  fullWidth,
  shouldUnregister
}: TextInputProps) => {
  const {
    register,
    formState: { errors }
  } = useFormContext();

  const intl = useIntl();

  const fieldError = idx(name.split("."), errors);

  return isLoading ? (
    <InputLoader fullWidth />
  ) : (
    <Input
      label={label}
      required={required}
      autoFocus={autoFocus}
      error={!!fieldError}
      helperText={fieldError?.message}
      dataTestId={dataTestId}
      InputProps={InputProps}
      inputProps={inputProps}
      placeholder={placeholder}
      multiline={multiline}
      rows={rows}
      type={type}
      autoComplete={autoComplete}
      margin={margin}
      sx={sx}
      minRows={minRows}
      maxRows={maxRows}
      disabled={disabled}
      defaultValue={defaultValue}
      isMasked={masked}
      className={className}
      fullWidth={fullWidth}
      {...register(name, {
        required: {
          value: required,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        },
        maxLength:
          maxLength !== null
            ? {
                value: maxLength,
                message: intl.formatMessage({ id: "maxFieldLength" }, { max: maxLength })
              }
            : undefined,
        minLength:
          minLength !== null
            ? { value: minLength, message: intl.formatMessage({ id: "minFieldLength" }, { min: minLength }) }
            : undefined,
        pattern,
        validate: {
          notOnlyWhiteSpaces,
          ...validate
        },
        shouldUnregister
      })}
    />
  );
};

export default TextInput;
