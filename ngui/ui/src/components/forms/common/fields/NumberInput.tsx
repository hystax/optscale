import { ReactNode } from "react";
import { useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import Input from "components/Input";
import InputLoader from "components/InputLoader";
import { MAX_INT_32 } from "utils/constants";
import { idx } from "utils/objects";
import { isNumber, notOnlyWhiteSpaces } from "utils/validation";

type NumberInputProps = {
  name: string;
  label?: ReactNode;
  required?: boolean;
  autoFocus?: boolean;
  dataTestId?: string;
  isLoading?: boolean;
  InputProps?: Record<string, unknown>;
  min?: number | null;
  max?: number | null;
  validate?: Record<string, unknown>;
  valueAsNumber?: boolean;
  type?: string;
  inputProps?: Record<string, unknown>;
  sx?: Record<string, unknown>;
  defaultValue?: string;
  margin?: "none" | "dense" | "normal";
  onChange?: (event: unknown) => void;
};

const NumberInput = ({
  name,
  label,
  required = false,
  autoFocus = false,
  dataTestId,
  isLoading = false,
  InputProps,
  min = null,
  max = MAX_INT_32,
  validate,
  valueAsNumber = false,
  inputProps,
  sx,
  defaultValue,
  margin,
  onChange
}: NumberInputProps) => {
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
      sx={sx}
      defaultValue={defaultValue}
      margin={margin}
      {...register(name, {
        required: {
          value: required,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        },
        min:
          min !== null
            ? {
                value: min,
                message: intl.formatMessage({ id: "moreOrEqual" }, { min })
              }
            : undefined,
        max:
          max !== null
            ? {
                value: max,
                message: intl.formatMessage({ id: "lessOrEqual" }, { max })
              }
            : undefined,
        validate: {
          notOnlyWhiteSpaces,
          isNumber: (value) => (isNumber(Number(value)) ? true : intl.formatMessage({ id: "fieldMustBeANumber" })),
          ...validate
        },
        valueAsNumber,
        onChange
      })}
    />
  );
};

export default NumberInput;
