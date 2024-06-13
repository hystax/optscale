import { Box, Link } from "@mui/material";
import { useForm, FormProvider } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import { ENVIRONMENTS } from "urls";
import { NameField, TypeField, SshRequiredField, FormButtons } from "./FormElements";
import PropertiesField from "./FormElements/PropertiesField";
import { CreateEnvironmentFormProps, FormValues } from "./types";
import { getDefaultValues } from "./utils";

const actionBarDefinition = {
  breadcrumbs: [
    <Link key={1} to={ENVIRONMENTS} component={RouterLink}>
      <FormattedMessage id="environments" />
    </Link>
  ],
  title: {
    text: <FormattedMessage id="addEnvironment" />,
    dataTestId: "lbl_add_environment"
  }
};

const CreateEnvironmentForm = ({ onSubmit, onCancel, isSubmitLoading = false }: CreateEnvironmentFormProps) => {
  const methods = useForm<FormValues>({
    defaultValues: getDefaultValues()
  });

  const { handleSubmit } = methods;

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Box sx={{ width: { xl: "50%" } }}>
          <FormProvider {...methods}>
            <form data-test-id="create_environment_form" onSubmit={handleSubmit(onSubmit)} noValidate>
              <NameField />
              <TypeField />
              <SshRequiredField />
              <PropertiesField />
              <FormButtons onCancel={onCancel} isLoading={isSubmitLoading} />
            </form>
          </FormProvider>
        </Box>
      </PageContentWrapper>
    </>
  );
};

export default CreateEnvironmentForm;
