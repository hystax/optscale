import { FormProvider, useForm } from "react-hook-form";
import RememberYourPasswordSignInMessage from "components/RememberYourPasswordSignInMessage";
import SendVerificationCodeAgainContainer from "containers/SendVerificationCodeAgainContainer";
import { getQueryParams } from "utils/network";
import { FIELD_NAMES } from "./constants";
import { CodeField, FormButtons } from "./FormElements";
import { FormValues, ConfirmVerificationCodeFormProps } from "./types";

const ConfirmVerificationCodeForm = ({ onSubmit, isLoading = false }: ConfirmVerificationCodeFormProps) => {
  const { code } = getQueryParams() as { code: string };

  const methods = useForm<FormValues>({
    defaultValues: {
      [FIELD_NAMES.CODE]: code ?? ""
    }
  });

  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form noValidate onSubmit={handleSubmit(onSubmit)}>
        <CodeField />
        <SendVerificationCodeAgainContainer />
        <FormButtons isLoading={isLoading} />
        <RememberYourPasswordSignInMessage />
      </form>
    </FormProvider>
  );
};

export default ConfirmVerificationCodeForm;
