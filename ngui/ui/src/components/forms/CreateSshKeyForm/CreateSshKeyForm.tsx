import Grid from "@mui/material/Grid";
import { FormProvider, useForm } from "react-hook-form";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import { SPACING_2 } from "utils/layouts";
import { FormButtons, SshKeyNameField, SshKeyValueField } from "./FormElements";
import { CreateSshKeyFormProps, FormValues } from "./types";
import { getDefaultValues } from "./utils";

const CreateSshKeyForm = ({ onSubmit, isSubmitLoading = false }: CreateSshKeyFormProps) => {
  const methods = useForm<FormValues>({
    defaultValues: getDefaultValues()
  });

  const { handleSubmit } = methods;

  return (
    <Grid container spacing={SPACING_2}>
      <Grid item xs={12}>
        <InlineSeverityAlert messageDataTestId="ssh-hint" messageId="sshHint" />
      </Grid>
      <Grid item>
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
      </Grid>
    </Grid>
  );
};

export default CreateSshKeyForm;
