import { useNavigate } from "react-router-dom";
import DisconnectCloudAccountForm from "components/forms/DisconnectCloudAccountForm";
import { getReasonValue } from "components/forms/DisconnectCloudAccountForm/utils";
import DataSourcesService, { DATASOURCE_SURVEY_TYPES } from "services/DataSourcesService";
import { CLOUD_ACCOUNTS } from "urls";

const DisconnectCloudAccountContainer = ({ id, type, parentId, onCancel }) => {
  const navigate = useNavigate();

  const { useDisconnectDataSource, useCreateSurvey, useIsLastDataSource } = DataSourcesService();

  const { isLoading: isDisconnectDataSourceLoading, disconnectDataSource } = useDisconnectDataSource();
  const disconnectAndRedirect = () => disconnectDataSource(id).then(() => navigate(CLOUD_ACCOUNTS));

  const { isLoading: isCreateSurveyLoading, createSurvey } = useCreateSurvey();

  const isLastDataSource = useIsLastDataSource();

  return (
    <DisconnectCloudAccountForm
      isLastDataSource={isLastDataSource}
      type={type}
      parentId={parentId}
      onCancel={onCancel}
      isLoading={isDisconnectDataSourceLoading || isCreateSurveyLoading}
      onSubmit={(formValues) => {
        const { reason, otherReason, missingCapabilities } = formValues;

        const isReasonSelected = !!reason;
        const isCapabilitiesAdded = !!formValues.missingCapabilities;

        if (isLastDataSource && (isReasonSelected || isCapabilitiesAdded)) {
          const data = {
            reason: isReasonSelected ? getReasonValue(reason) : undefined,
            other: otherReason,
            capabilities: missingCapabilities
          };
          createSurvey(DATASOURCE_SURVEY_TYPES.DISCONNECT_LAST_DATA_SOURCE, data).then(disconnectAndRedirect);
        } else {
          disconnectAndRedirect();
        }
      }}
    />
  );
};

export default DisconnectCloudAccountContainer;
