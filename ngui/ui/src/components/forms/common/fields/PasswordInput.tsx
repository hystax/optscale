import { ReactNode, useState, useRef } from "react";
import RemoveRedEyeOutlinedIcon from "@mui/icons-material/RemoveRedEyeOutlined";
import VisibilityOffOutlinedIcon from "@mui/icons-material/VisibilityOffOutlined";
import { type SxProps, type Theme } from "@mui/material";
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
  sx?: SxProps<Theme>;
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
  sx,
}: PasswordInputProps) => {
  const {
    register,
    formState: { errors },
  } = useFormContext();

  const intl = useIntl();
  const inputRef = useRef();

  const { ref, ...rest } = register(name, {
    required: {
      value: required,
      message: intl.formatMessage({ id: "thisFieldIsRequired" }),
    },
    maxLength:
      maxLength !== null
        ? {
            value: maxLength,
            message: intl.formatMessage({ id: "maxFieldLength" }, { max: maxLength }),
          }
        : undefined,
    minLength:
      minLength !== null
        ? { value: minLength, message: intl.formatMessage({ id: "minFieldLength" }, { min: minLength }) }
        : undefined,
    validate,
  });

  const [shouldShowPassword, setShouldShowPassword] = useState(false);

  const { endAdornment, ...restInputProps } = InputProps;

  const fieldError = idx(name.split("."), errors);

  return isLoading ? (
    <InputLoader fullWidth />
  ) : (
    <Input
      label={label}
      ref={(e) => {
        ref(e);
        inputRef.current = e;
      }}
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
              onClick={() => {
                inputRef.current.focus();
                setShouldShowPassword((currentState) => !currentState);
              }}
            />
            {endAdornment}
          </>
        ),
        ...restInputProps,
      }}
      {...rest}
    />
  );
};

export default PasswordInput;
