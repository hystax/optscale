import CheckCircleOutlinedIcon from "@mui/icons-material/CheckCircleOutlined";
import Box from "@mui/material/Box";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import { FormProvider, useForm } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ButtonLoader from "components/ButtonLoader";
import { LOGIN } from "urls";
import { SUCCESS } from "utils/constants";
import { EmailField } from "./FormElements";
import useStyles from "./ResetPasswordForm.styles";
import { FormValues, ResetPasswordFormProps } from "./types";

const ResetPasswordForm = ({ onSubmit, sendState, isLoading = false }: ResetPasswordFormProps) => {
  const { classes } = useStyles();

  const methods = useForm<FormValues>();

  const { handleSubmit } = methods;

  return (
    <div>
      {sendState === SUCCESS ? (
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
      ) : (
        <Box>
          <Box display="flex" flexDirection="column" alignItems="center" mb={3}>
            <Typography>
              <FormattedMessage id="resetPasswordInstructions" />
            </Typography>
          </Box>
          <FormProvider {...methods}>
            <form onSubmit={handleSubmit(onSubmit)} noValidate>
              <EmailField />
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
          </FormProvider>
        </Box>
      )}
    </div>
  );
};

export default ResetPasswordForm;
