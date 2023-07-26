import React from "react";
import Box from "@mui/material/Box";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { useForm } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import { Link as RouterLink, useLocation } from "react-router-dom";
import ButtonLoader from "components/ButtonLoader";
import Input from "components/Input";
import PasswordInput from "components/PasswordInput";
import { HYSTAX_PRIVACY_POLICY, LOGIN } from "urls";
import { getQueryParams } from "utils/network";
import { emailRegex } from "utils/strings";
import { notOnlyWhiteSpaces } from "../../utils/validation";
import useStyles from "./RegistrationForm.styles";

const MAX_LENGTH = 255;
const FULL_NAME_MAX_LENGTH = 64;

const RegistrationForm = ({ onSubmit, isLoading = false, isInvited }) => {
  const intl = useIntl();
  const { classes } = useStyles();
  const { email } = getQueryParams();

  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm();

  const { search } = useLocation();

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      <Input
        required
        dataTestId="input_email"
        defaultValue={email}
        error={!!errors.email}
        helperText={errors.email && errors.email.message}
        label={<FormattedMessage id="businessLogin" />}
        type="email"
        autoComplete="username email"
        margin="normal"
        InputProps={{
          readOnly: isInvited
        }}
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
              { inputName: intl.formatMessage({ id: "businessLogin" }), max: MAX_LENGTH }
            )
          }
        })}
      />
      <Input
        required
        dataTestId="input_full_name"
        error={!!errors.name}
        helperText={errors.name && errors.name.message}
        label={<FormattedMessage id="fullName" />}
        type="text"
        margin="normal"
        autoComplete="name"
        {...register("name", {
          required: {
            value: true,
            message: intl.formatMessage({ id: "thisFieldIsRequired" })
          },
          maxLength: {
            value: FULL_NAME_MAX_LENGTH,
            message: intl.formatMessage(
              { id: "maxLength" },
              { inputName: intl.formatMessage({ id: "fullName" }), max: FULL_NAME_MAX_LENGTH }
            )
          },
          validate: {
            notOnlyWhiteSpaces
          }
        })}
      />
      <PasswordInput
        required
        error={!!errors.password}
        helperText={errors.password && errors.password.message}
        dataTestId="input_pass"
        label={<FormattedMessage id="password" />}
        margin="normal"
        autoComplete="new-password"
        {...register("password", {
          required: {
            value: true,
            message: intl.formatMessage({ id: "thisFieldIsRequired" })
          },
          minLength: {
            value: 6,
            message: intl.formatMessage({ id: "passwordValidationRules" })
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
      <PasswordInput
        required
        dataTestId="input_conf_pass"
        error={!!errors.confirmPassword}
        helperText={errors.confirmPassword && errors.confirmPassword.message}
        label={<FormattedMessage id="confirmPassword" />}
        margin="normal"
        autoComplete="new-password"
        {...register("confirmPassword", {
          required: {
            value: true,
            message: intl.formatMessage({ id: "thisFieldIsRequired" })
          },
          validate: (value, formValues) => value === formValues.password || intl.formatMessage({ id: "passwordsDoNotMatch" })
        })}
      />
      <Typography data-test-id="p_no_credit" align="center">
        <FormattedMessage id="noCreditCardRequired" />
      </Typography>
      <Box className={classes.registerButtonWrapper}>
        <ButtonLoader
          uppercase
          dataTestId="btn_register"
          variant="contained"
          color="lightBlue"
          customWrapperClass={classes.registerButton}
          isLoading={isLoading}
          messageId="register"
          type="submit"
          size="large"
          fullWidth
        />
        <Typography variant="caption" align="center" component="div">
          <FormattedMessage
            id="agreeToHystaxPrivacyPolicyUponRegistration"
            values={{
              link: (chunks) => (
                <Link data-test-id="link_privacy_policy" href={HYSTAX_PRIVACY_POLICY} target="_blank" rel="noopener">
                  {chunks}
                </Link>
              )
            }}
          />
        </Typography>
      </Box>
      <Box display="flex" justifyContent="center">
        <Typography>
          <Link data-test-id="link_sign_in" color="primary" to={`${LOGIN}${search}`} component={RouterLink}>
            {<FormattedMessage id="haveAccountSignIn" />}
          </Link>
        </Typography>
      </Box>
    </form>
  );
};

RegistrationForm.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  isLoading: PropTypes.bool,
  isInvited: PropTypes.bool
};

export default RegistrationForm;
