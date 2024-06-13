import { Box } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import DeleteEntity from "components/DeleteEntity";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import { useDataSources } from "hooks/useDataSources";
import { AZURE_TENANT } from "utils/constants";
import { SPACING_1 } from "utils/layouts";
import Survey from "./FormElements/Survey";
import { DisconnectCloudAccountFormProps, FormValues } from "./types";
import { getDefaultValues } from "./utils";

const DisconnectCloudAccountForm = ({
  type,
  parentId,
  onSubmit,
  onCancel,
  isLoading = false,
  isLastDataSource = false
}: DisconnectCloudAccountFormProps) => {
  const { disconnectQuestionId } = useDataSources(type);
  const isAzureTenant = type === AZURE_TENANT;

  const methods = useForm<FormValues>({ defaultValues: getDefaultValues() });
  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form data-test-id="disconnect-datasource-form" onSubmit={handleSubmit(onSubmit)} noValidate>
        {(parentId || isAzureTenant) && (
          <Box mb={SPACING_1}>
            {parentId && <InlineSeverityAlert messageId="childDataSourceDisconnectionWarning" />}
            {isAzureTenant && <InlineSeverityAlert messageId="parentDataSourceDisconnectionWarning" />}
          </Box>
        )}
        <DeleteEntity
          message={{
            messageId: isLastDataSource ? undefined : disconnectQuestionId
          }}
          dataTestIds={{
            text: "p_disconnect",
            cancelButton: "btn_cancel",
            deleteButton: "btn_disconnect_data_source"
          }}
          isLoading={isLoading}
          deleteButtonProps={{
            messageId: "disconnect"
          }}
          onCancel={onCancel}
        >
          {isLastDataSource && <Survey />}
        </DeleteEntity>
      </form>
    </FormProvider>
  );
};

export default DisconnectCloudAccountForm;
