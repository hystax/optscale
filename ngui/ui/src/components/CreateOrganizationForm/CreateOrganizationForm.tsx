import { Typography } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import { CreateOrganizationFormNameInput, NAME_FIELD_NAME } from "./FormElements";

const CreateOrganizationForm = ({ onSubmit, onCancel, isLoading }) => {
  const methods = useForm({
    defaultValues: {
      [NAME_FIELD_NAME]: ""
    }
  });

  const { handleSubmit } = methods;

  return (
    <>
      <Typography paragraph>
        <FormattedMessage id="createNewOrganizationDescription" />
      </Typography>
      <FormProvider {...methods}>
        <form
          onSubmit={handleSubmit((formData) => {
            onSubmit(formData[NAME_FIELD_NAME]);
          })}
          noValidate
        >
          <CreateOrganizationFormNameInput />
          <FormButtonsWrapper>
            <ButtonLoader
              dataTestId="btn_create_new_organization"
              messageId="create"
              color="primary"
              variant="contained"
              isLoading={isLoading}
              type="submit"
            />
            <Button dataTestId="btn_cancel_cloud_account" messageId="cancel" onClick={onCancel} />
          </FormButtonsWrapper>
        </form>
      </FormProvider>
    </>
  );
};

export default CreateOrganizationForm;
