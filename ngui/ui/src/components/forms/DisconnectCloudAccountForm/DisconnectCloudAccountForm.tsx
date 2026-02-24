import { Box } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import DeleteEntity from "components/DeleteEntity";
import PageContentDescription from "components/PageContentDescription";
import { useDataSources } from "hooks/useDataSources";
import { useOrganizationActionRestrictions } from "hooks/useOrganizationActionRestrictions";
import { AZURE_TENANT, GCP_TENANT } from "utils/constants";
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
  isLastDataSource = false,
}: DisconnectCloudAccountFormProps) => {
  const { isRestricted, restrictionReasonMessage } = useOrganizationActionRestrictions();

  const { disconnectQuestionId } = useDataSources(type);
  const isAzureTenant = type === AZURE_TENANT;
  const isGcpTenant = type === GCP_TENANT;

  const methods = useForm<FormValues>({ defaultValues: getDefaultValues() });
  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form data-test-id="disconnect-datasource-form" onSubmit={handleSubmit(onSubmit)} noValidate>
        {(parentId || isAzureTenant || isGcpTenant) && (
          <Box mb={SPACING_1}>
            {parentId && (
              <PageContentDescription
                position="top"
                alertProps={{
                  messageId: "childDataSourceDisconnectionWarning",
                }}
              />
            )}
            {isAzureTenant || isGcpTenant ? (
              <PageContentDescription
                position="top"
                alertProps={{
                  messageId: "parentDataSourceDisconnectionWarning",
                }}
              />
            ) : null}
          </Box>
        )}
        <DeleteEntity
          message={{
            messageId: isLastDataSource ? undefined : disconnectQuestionId,
          }}
          dataTestIds={{
            text: "p_disconnect",
            cancelButton: "btn_cancel",
            deleteButton: "btn_disconnect_data_source",
          }}
          isLoading={isLoading}
          deleteButtonProps={{
            messageId: "disconnect",
            disabled: isRestricted,
            tooltip: {
              show: isRestricted,
              value: restrictionReasonMessage,
            },
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
