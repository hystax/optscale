import { FormProvider, useForm } from "react-hook-form";
import RememberYourPasswordSignInMessage from "components/RememberYourPasswordSignInMessage";
import { getQueryParams } from "utils/network";
import { FIELD_NAMES } from "./constants";
import { ConfirmPasswordField, EmailField, FormButtons, NewPasswordField } from "./FormElements";
import { FormValues, CreateNewPasswordFormProps } from "./types";

const CreateNewPasswordForm = ({ onSubmit, isLoading = false }: CreateNewPasswordFormProps) => {
  const { email } = getQueryParams() as { email: string };

  const methods = useForm<FormValues>({
    defaultValues: {
      [FIELD_NAMES.EMAIL]: email
    }
  });

  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <EmailField />
        <NewPasswordField />
        <ConfirmPasswordField />
        <FormButtons isLoading={isLoading} />
        <RememberYourPasswordSignInMessage />
      </form>
    </FormProvider>
  );
};

export default CreateNewPasswordForm;
