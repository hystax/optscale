import Box from "@mui/material/Box";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import { FormProvider, useForm } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ButtonLoader from "components/ButtonLoader";
import { REGISTER } from "urls";
import { getQueryParams, getSearch } from "utils/network";
import { EmailField, PasswordField } from "./FormElements";
import useStyles from "./LoginForm.styles";
import { FormValues, LoginFormProps } from "./types";
import { getDefaultValues } from "./utils";

const LoginForm = ({ onSubmit, isLoading = false, isInvited = false }: LoginFormProps) => {
  const { classes } = useStyles();

  const { email = "" } = getQueryParams() as { email?: string };

  const methods = useForm<FormValues>({
    defaultValues: getDefaultValues({
      email
    })
  });

  const { handleSubmit } = methods;

  const search = getSearch();

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <EmailField readOnly={isInvited} />
        <PasswordField />
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
          {/* <Link color="primary" to={RESET_PASSWORD} component={RouterLink}>
            {<FormattedMessage id="forgotPassword" />}
          </Link> */}
          <Typography>
            <Link data-test-id="link_sign_up" color="primary" to={`${REGISTER}${search}`} component={RouterLink}>
              {<FormattedMessage id="noAccountSignUp" />}
            </Link>
          </Typography>
        </Box>
      </form>
    </FormProvider>
  );
};

export default LoginForm;
