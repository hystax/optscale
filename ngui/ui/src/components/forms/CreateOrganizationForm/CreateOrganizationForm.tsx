import { Typography } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import { NameField, FormButtons } from "./FormElements";
import { CreateOrganizationFormProps, FormValues } from "./types";
import { getDefaultValues } from "./utils";

const CreateOrganizationForm = ({ onSubmit, onCancel, isLoading }: CreateOrganizationFormProps) => {
  const methods = useForm<FormValues>({
    defaultValues: getDefaultValues(),
  });

  return (
    <>
      <FormProvider {...methods}>
        <form onSubmit={methods.handleSubmit(onSubmit)} noValidate>
          <Typography gutterBottom>
            <FormattedMessage id="createNewOrganizationDescription" />
          </Typography>
          <NameField />
          <FormButtons onCancel={onCancel} isLoading={isLoading} />
        </form>
      </FormProvider>
    </>
  );
};

export default CreateOrganizationForm;
