import { ReactNode, useState } from "react";
import RemoveRedEyeOutlinedIcon from "@mui/icons-material/RemoveRedEyeOutlined";
import VisibilityOffOutlinedIcon from "@mui/icons-material/VisibilityOffOutlined";
import { useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import IconButton from "components/IconButton";
import Input from "components/Input";
import InputLoader from "components/InputLoader";
import { DEFAULT_MAX_INPUT_LENGTH } from "utils/constants";
import { idx } from "utils/objects";

type PasswordInputProps = {
  name: string;
  label?: ReactNode;
  required?: boolean;
  InputProps?: Record<string, unknown>;
  maxLength?: number | null;
  minLength?: number | null;
  validate?: Record<string, unknown>;
  isLoading?: boolean;
  dataTestId?: string;
  margin?: "none" | "dense" | "normal";
  autoComplete?: string;
  sx?: Record<string, unknown>;
};

const PasswordInput = ({
  name,
  label,
  required = false,
  InputProps = {},
  maxLength = DEFAULT_MAX_INPUT_LENGTH,
  minLength = null,
  validate,
  isLoading = false,
  dataTestId,
  margin,
  autoComplete,
  sx
}: PasswordInputProps) => {
  const {
    register,
    formState: { errors }
  } = useFormContext();

  const intl = useIntl();

  const [shouldShowPassword, setShouldShowPassword] = useState(false);

  const { endAdornment, ...restInputProps } = InputProps;

  const fieldError = idx(name.split("."), errors);

  return isLoading ? (
    <InputLoader fullWidth />
  ) : (
    <Input
      label={label}
      type={shouldShowPassword ? "text" : "password"}
      error={!!fieldError}
      helperText={fieldError?.message}
      dataTestId={dataTestId}
      margin={margin}
      autoComplete={autoComplete}
      sx={sx}
      InputProps={{
        endAdornment: (
          <>
            <IconButton
              tooltip={{ show: true, messageId: shouldShowPassword ? "hidePassword" : "showPassword" }}
              key="eyeButton"
              icon={shouldShowPassword ? <VisibilityOffOutlinedIcon /> : <RemoveRedEyeOutlinedIcon />}
              color="primary"
              onClick={() => setShouldShowPassword((currentState) => !currentState)}
            />
            {endAdornment}
          </>
        ),
        ...restInputProps
      }}
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
        validate
      })}
    />
  );
};

export default PasswordInput;
