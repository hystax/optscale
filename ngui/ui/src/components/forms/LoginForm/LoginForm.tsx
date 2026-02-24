import Box from "@mui/material/Box";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import { FormProvider, useForm } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import { REGISTER, PASSWORD_RECOVERY, OPTSCALE_CAPABILITY_QUERY_PARAMETER_NAME } from "urls";
import { stringifySearchParams, getSearchParams, getSearch } from "utils/network";
import { EmailField, FormButtons, PasswordField } from "./FormElements";
import { FormValues, LoginFormProps } from "./types";
import { getDefaultValues } from "./utils";

const LoginForm = ({ onSubmit, isLoading = false, disabled = false, isInvited = false }: LoginFormProps) => {
  const { email = "", [OPTSCALE_CAPABILITY_QUERY_PARAMETER_NAME]: capability } = getSearchParams() as {
    email?: string;
    [OPTSCALE_CAPABILITY_QUERY_PARAMETER_NAME]: string;
  };

  const methods = useForm<FormValues>({
    defaultValues: getDefaultValues({
      email,
    }),
  });

  const { handleSubmit } = methods;

  const search = getSearch();

  const passwordRecoveryUrl = `${PASSWORD_RECOVERY}?${stringifySearchParams({
    [OPTSCALE_CAPABILITY_QUERY_PARAMETER_NAME]: capability,
  })}`;

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <EmailField readOnly={isInvited} />
        <PasswordField />
        <FormButtons isLoading={isLoading} disabled={disabled} />
        <Box display="flex" justifyContent="space-evenly">
          <Typography>
            <Link color="primary" to={passwordRecoveryUrl} component={RouterLink}>
              <FormattedMessage id="forgotPassword" />
            </Link>
          </Typography>
          <Typography>
            <Link data-test-id="link_sign_up" color="primary" to={`${REGISTER}${search}`} component={RouterLink}>
              <FormattedMessage id="noAccountSignUp" />
            </Link>
          </Typography>
        </Box>
      </form>
    </FormProvider>
  );
};

export default LoginForm;
