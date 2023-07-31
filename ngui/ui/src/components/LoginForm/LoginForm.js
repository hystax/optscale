import React from "react";
import Box from "@mui/material/Box";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { useForm } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ButtonLoader from "components/ButtonLoader";
import Input from "components/Input";
import PasswordInput from "components/PasswordInput";
import { REGISTER } from "urls";
import { getQueryParams, getSearch } from "utils/network";
import { emailRegex } from "utils/strings";
import useStyles from "./LoginForm.styles";

const MAX_LENGTH = 255;

const LoginForm = ({ onSubmit, isLoading, isInvited }) => {
  const { classes } = useStyles();
  const intl = useIntl();

  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm();

  const search = getSearch();
  const { email } = getQueryParams();

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      <Input
        required
        dataTestId="input_email"
        InputProps={{
          readOnly: isInvited
        }}
        defaultValue={email}
        error={!!errors.email}
        helperText={errors.email && errors.email.message}
        label={<FormattedMessage id="userLogin" />}
        type="email"
        autoComplete="email"
        margin="normal"
        {...register("email", {
          required: {
            value: true,
            message: intl.formatMessage({ id: "thisFieldIsRequired" })
          },
          pattern: {
            value: emailRegex,
            message: intl.formatMessage({ id: "invalidEmailAddress" })
          },
          maxLength: {
            value: MAX_LENGTH,
            message: intl.formatMessage(
              { id: "maxLength" },
              { inputName: intl.formatMessage({ id: "userLogin" }), max: MAX_LENGTH }
            )
          }
        })}
      />
      <PasswordInput
        dataTestId="input_pass"
        required
        error={!!errors.password}
        helperText={errors.password && errors.password.message}
        label={<FormattedMessage id="password" />}
        autoComplete="current-password"
        margin="normal"
        {...register("password", {
          required: {
            value: true,
            message: intl.formatMessage({ id: "thisFieldIsRequired" })
          },
          maxLength: {
            value: MAX_LENGTH,
            message: intl.formatMessage(
              { id: "maxLength" },
              { inputName: intl.formatMessage({ id: "password" }), max: MAX_LENGTH }
            )
          }
        })}
      />
      <ButtonLoader
        dataTestId="btn_login"
        uppercase
        variant="contained"
        color="lightBlue"
        customWrapperClass={classes.submitButtonWrapper}
        isLoading={isLoading}
        messageId="login"
        type="submit"
        size="large"
        fullWidth
      />
      <Box display="flex" justifyContent="center">
        {/*
        <Link color="primary" to={RESET_PASSWORD} component={RouterLink}>
          {<FormattedMessage id="forgotPassword" />}
        </Link>
        */}
        <Typography>
          <Link data-test-id="link_sign_up" color="primary" to={`${REGISTER}${search}`} component={RouterLink}>
            {<FormattedMessage id="noAccountSignUp" />}
          </Link>
        </Typography>
      </Box>
    </form>
  );
};

LoginForm.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  isLoading: PropTypes.bool.isRequired,
  isInvited: PropTypes.bool.isRequired
};

export default LoginForm;
