import { Typography } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import { NameField } from "./FormElements";
import FormButtons from "./FormElements/FormButtons";
import { CreateOrganizationFormProps, FormValues } from "./types";
import { getDefaultValues } from "./utils";

const CreateOrganizationForm = ({ onSubmit, onCancel, isLoading }: CreateOrganizationFormProps) => {
  const methods = useForm<FormValues>({
    defaultValues: getDefaultValues()
  });

  const { handleSubmit } = methods;

  return (
    <>
      <Typography paragraph>
        <FormattedMessage id="createNewOrganizationDescription" />
      </Typography>
      <FormProvider {...methods}>
        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <NameField />
          <FormButtons onCancel={onCancel} isLoading={isLoading} />
        </form>
      </FormProvider>
    </>
  );
};

export default CreateOrganizationForm;
