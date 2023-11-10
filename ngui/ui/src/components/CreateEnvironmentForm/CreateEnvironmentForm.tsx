import { Box, Link } from "@mui/material";
import { useForm, FormProvider } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import Button from "components/Button";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import PageContentWrapper from "components/PageContentWrapper";
import SubmitButtonLoader from "components/SubmitButtonLoader";
import { ENVIRONMENTS } from "urls";
import {
  CreateEnvironmentFormNameField,
  CreateEnvironmentFormPropertiesField,
  CreateEnvironmentFormTypeField,
  CreateEnvironmentFormSshRequiredField
} from "./FormElements";

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

const PROPERTIES = "properties";
const PROPERTY_NAME = "propertyName";
const PROPERTY_VALUE = "propertyValue";

const CreateEnvironmentForm = ({ onSubmit, onCancel, isSubmitLoading = false }) => {
  const methods = useForm({
    defaultValues: {
      [PROPERTIES]: [
        { [PROPERTY_NAME]: "Description", [PROPERTY_VALUE]: "" },
        { [PROPERTY_NAME]: "IP", [PROPERTY_VALUE]: "" },
        { [PROPERTY_NAME]: "Software", [PROPERTY_VALUE]: "" }
      ]
    }
  });
  const { handleSubmit } = methods;

  const onSubmitHandler = handleSubmit((formData) => {
    const { [PROPERTIES]: properties, ...rest } = formData;

    onSubmit({
      properties: Object.fromEntries(properties.map(({ [PROPERTY_NAME]: name, [PROPERTY_VALUE]: value }) => [name, value])),
      ...rest
    });
  });

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Box sx={{ width: { xl: "50%" } }}>
          <FormProvider {...methods}>
            <form data-test-id="create_environment_form" onSubmit={onSubmitHandler} noValidate>
              <CreateEnvironmentFormNameField />
              <CreateEnvironmentFormTypeField />
              <CreateEnvironmentFormSshRequiredField />
              <CreateEnvironmentFormPropertiesField
                fieldName={PROPERTIES}
                propertyFieldNames={{ name: PROPERTY_NAME, value: PROPERTY_VALUE }}
              />
              <FormButtonsWrapper>
                <SubmitButtonLoader
                  messageId="create"
                  isLoading={isSubmitLoading}
                  dataTestId="btn_create"
                  loaderDataTestId="btn_create_loader"
                />
                <Button messageId="cancel" onClick={onCancel} dataTestId="btn_cancel" />
              </FormButtonsWrapper>
            </form>
          </FormProvider>
        </Box>
      </PageContentWrapper>
    </>
  );
};

export default CreateEnvironmentForm;
