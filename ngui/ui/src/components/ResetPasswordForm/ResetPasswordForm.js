import React from "react";
import CheckCircleOutlinedIcon from "@mui/icons-material/CheckCircleOutlined";
import Box from "@mui/material/Box";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { useForm } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ButtonLoader from "components/ButtonLoader";
import Input from "components/Input";
import { LOGIN } from "urls";
import { SUCCESS } from "utils/constants";
import { emailRegex } from "utils/strings";
import useStyles from "./ResetPasswordForm.styles";

const ResetPasswordForm = ({ onSubmit, isLoading, sendState }) => {
  const { classes } = useStyles();
  const intl = useIntl();

  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm();

  const renderConfirmationTemplate = (
    // TODO - create a separate component
    <Box display="flex" flexDirection="column" alignItems="center">
      <CheckCircleOutlinedIcon className={classes.successIcon} />
      <Typography>
        <FormattedMessage id="resetPasswordConfirmationMessage" />{" "}
        <FormattedMessage
          id="linkExpirationMessage"
          values={{
            count: 12,
            value: "hours",
            strong: (chunks) => <strong>{chunks}</strong>
          }}
        />
      </Typography>
    </Box>
  );

  return (
    <div>
      {sendState === SUCCESS ? (
        renderConfirmationTemplate
      ) : (
        <Box>
          <Box display="flex" flexDirection="column" alignItems="center" mb={3}>
            <Typography>
              <FormattedMessage id="resetPasswordInstructions" />
            </Typography>
          </Box>
          <form onSubmit={handleSubmit(onSubmit)} noValidate>
            <Input
              required
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
                }
              })}
            />
            <ButtonLoader
              variant="contained"
              color="primary"
              customWrapperClass={classes.submitButtonWrapper}
              isLoading={isLoading}
              messageId="sendLink"
              type="submit"
              size="large"
              fullWidth
            />
            <Box display="flex" justifyContent="center">
              <Link color="primary" to={LOGIN} component={RouterLink}>
                {<FormattedMessage id="backToLogin" />}
              </Link>
            </Box>
          </form>
        </Box>
      )}
    </div>
  );
};

ResetPasswordForm.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  isLoading: PropTypes.bool.isRequired,
  sendState: PropTypes.string.isRequired
};

export default ResetPasswordForm;
