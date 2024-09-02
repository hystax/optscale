import { FormProvider, useForm } from "react-hook-form";
import RememberYourPasswordSignInMessage from "components/RememberYourPasswordSignInMessage";
import { EmailField, FormButtons } from "./FormElements";
import { FormValues, SendVerificationCodeFormProps } from "./types";

const SendVerificationCodeForm = ({ onSubmit, isLoading = false }: SendVerificationCodeFormProps) => {
  const methods = useForm<FormValues>();

  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <EmailField />
        <FormButtons isLoading={isLoading} />
        <RememberYourPasswordSignInMessage />
      </form>
    </FormProvider>
  );
};

export default SendVerificationCodeForm;
