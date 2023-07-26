import React, { useState, useRef, forwardRef } from "react";
import RemoveRedEyeOutlinedIcon from "@mui/icons-material/RemoveRedEyeOutlined";
import VisibilityOffOutlinedIcon from "@mui/icons-material/VisibilityOffOutlined";
import IconButton from "components/IconButton";
import Input from "components/Input";

const PasswordInput = ({ InputProps = {}, ...rest }, ref) => {
  const [shouldShowPassword, setShouldShowPassword] = useState(false);
  const showPasswordButtonRef = useRef();

  const { endAdornment, ...restInputProps } = InputProps;

  return (
    <Input
      type={shouldShowPassword ? "text" : "password"}
      ref={ref}
      InputProps={{
        endAdornment: (
          <>
            <IconButton
              ref={showPasswordButtonRef}
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
      {...rest}
    />
  );
};

const ForwardedPasswordInput = forwardRef(PasswordInput);

export default ForwardedPasswordInput;
