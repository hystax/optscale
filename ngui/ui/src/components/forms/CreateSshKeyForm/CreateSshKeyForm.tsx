import { FormProvider, useForm } from "react-hook-form";
import PageContentDescription from "components/PageContentDescription/PageContentDescription";
import { FormButtons, SshKeyNameField, SshKeyValueField } from "./FormElements";
import { CreateSshKeyFormProps, FormValues } from "./types";
import { getDefaultValues } from "./utils";

const CreateSshKeyForm = ({ onSubmit, isSubmitLoading = false }: CreateSshKeyFormProps) => {
  const methods = useForm<FormValues>({
    defaultValues: getDefaultValues(),
  });

  const { handleSubmit } = methods;

  return (
    <>
      <PageContentDescription
        position="top"
        alertProps={{
          messageId: "sshHint",
          messageDataTestId: "ssh-hint",
        }}
      />
      <FormProvider {...methods}>
        <form
          onSubmit={handleSubmit((data) => {
            onSubmit(data);
            methods.reset(); // TODO: reset only on success
          })}
          noValidate
        >
          <SshKeyNameField />
          <SshKeyValueField />
          <FormButtons isLoading={isSubmitLoading} />
        </form>
      </FormProvider>
    </>
  );
};

export default CreateSshKeyForm;
