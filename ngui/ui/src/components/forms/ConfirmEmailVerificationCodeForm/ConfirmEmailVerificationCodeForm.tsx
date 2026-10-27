import { FormProvider, useForm } from "react-hook-form";
import AlreadyHaveAnAccountSignInMessage from "components/AlreadyHaveAnAccountSignInMessage";
import SendEmailVerificationCodeAgainContainer from "containers/SendEmailVerificationCodeAgainContainer";
import { getSearchParams } from "utils/network";
import { FIELD_NAMES } from "./constants";
import { CodeField, FormButtons } from "./FormElements";
import { FormValues, ConfirmEmailVerificationCodeFormProps } from "./types";

const ConfirmEmailVerificationCodeForm = ({ onSubmit, isLoading = false }: ConfirmEmailVerificationCodeFormProps) => {
  const { code } = getSearchParams({
    parseNumbers: false,
  }) as { code: string };

  const methods = useForm<FormValues>({
    defaultValues: {
      [FIELD_NAMES.CODE]: code ?? "",
    },
  });

  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form noValidate onSubmit={handleSubmit(onSubmit)}>
        <CodeField />
        <SendEmailVerificationCodeAgainContainer />
        <FormButtons isLoading={isLoading} />
        <AlreadyHaveAnAccountSignInMessage />
      </form>
    </FormProvider>
  );
};

export default ConfirmEmailVerificationCodeForm;
