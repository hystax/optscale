import { Stack } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import { DataSourceNameField, DATA_SOURCE_NAME_FIELD_NAME } from "components/DataSourceNameField";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import { SPACING_1 } from "utils/layouts";

const RenameDataSourceForm = ({ name, onSubmit, onCancel, isLoading = false }) => {
  const methods = useForm({
    defaultValues: {
      name
    }
  });

  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form
        onSubmit={handleSubmit(async (formData) => {
          onSubmit(formData[DATA_SOURCE_NAME_FIELD_NAME]);
        })}
        noValidate
      >
        <Stack spacing={SPACING_1}>
          <div>
            <DataSourceNameField />
          </div>
          <div>
            <InlineSeverityAlert messageId="dataSourceRenamingWarning" />
          </div>
        </Stack>
        <FormButtonsWrapper>
          <ButtonLoader
            dataTestId="btn_rename_data_source"
            loaderDataTestId="loading_btn_rename_data_source"
            messageId="save"
            color="primary"
            variant="contained"
            type="submit"
            isLoading={isLoading}
          />
          <Button dataTestId="btn_cancel_rename_data_source" messageId="cancel" onClick={onCancel} />
        </FormButtonsWrapper>
      </form>
    </FormProvider>
  );
};

export default RenameDataSourceForm;
