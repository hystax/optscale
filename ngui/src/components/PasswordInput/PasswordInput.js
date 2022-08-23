import React, { useState, useRef, forwardRef } from "react";
import RemoveRedEyeOutlinedIcon from "@mui/icons-material/RemoveRedEyeOutlined";
import VisibilityOffOutlinedIcon from "@mui/icons-material/VisibilityOffOutlined";
import PropTypes from "prop-types";
import IconButton from "components/IconButton";
import Input from "components/Input";

const PasswordInput = ({ onFocus, onBlur, ...rest }, ref) => {
  const [shouldShowPassword, setShouldShowPassword] = useState(false);

  const [shouldShowButton, setShouldShowButton] = useState(false);

  const showPasswordButtonRef = useRef();

  const resetState = () => {
    setShouldShowButton(false);
    setShouldShowPassword(false);
  };

  return (
    <Input
      onFocus={(event) => {
        setShouldShowButton(true);
        if (typeof onFocus === "function") {
          onFocus(event);
        }
      }}
      onBlur={(event) => {
        if (showPasswordButtonRef.current !== event.relatedTarget) {
          resetState();
        }
        if (typeof onBlur === "function") {
          onBlur(event);
        }
      }}
      type={shouldShowPassword ? "text" : "password"}
      ref={ref}
      InputProps={{
        endAdornment: shouldShowButton && (
          <IconButton
            ref={showPasswordButtonRef}
            tooltip={{ show: true, messageId: shouldShowPassword ? "hidePassword" : "showPassword" }}
            key="eyeButton"
            icon={shouldShowPassword ? <VisibilityOffOutlinedIcon /> : <RemoveRedEyeOutlinedIcon />}
            color="primary"
            onBlur={() => {
              resetState();
            }}
            onClick={() => setShouldShowPassword((currentState) => !currentState)}
          />
        )
      }}
      {...rest}
    />
  );
};

const ForwardedPasswordInput = forwardRef(PasswordInput);

ForwardedPasswordInput.propTypes = {
  onBlur: PropTypes.func,
  onFocus: PropTypes.func
};

export default ForwardedPasswordInput;
