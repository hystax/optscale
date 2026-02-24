import { useNavigate } from "react-router-dom";
import { GET_AVAILABLE_FILTERS } from "api/restapi/actionTypes";
import DisconnectCloudAccountForm from "components/forms/DisconnectCloudAccountForm";
import { getReasonValue } from "components/forms/DisconnectCloudAccountForm/utils";
import { DataSourcesDocument, useDeleteDataSourceMutation } from "graphql/__generated__/hooks/restapi";
import { useAllDataSources } from "hooks/coreData/useAllDataSources";
import { useRefetchApis } from "hooks/useRefetchApis";
import DataSourcesService, { DATASOURCE_SURVEY_TYPES } from "services/DataSourcesService";
import { CLOUD_ACCOUNTS } from "urls";
import { ENVIRONMENT } from "utils/constants";

type DisconnectCloudAccountContainerProps = {
  id: string;
  type: string;
  parentId: string;
  onCancel: () => void;
};

const useIsLastDataSource = () => {
  const dataSources = useAllDataSources();

  return dataSources.filter(({ type }) => type !== ENVIRONMENT).length === 1;
};

const DisconnectCloudAccountContainer = ({ id, type, parentId, onCancel }: DisconnectCloudAccountContainerProps) => {
  const refetch = useRefetchApis();
  const navigate = useNavigate();

  const { useCreateSurvey } = DataSourcesService();

  const [deleteDataSource, { loading: isDisconnectDataSourceLoading }] = useDeleteDataSourceMutation({
    refetchQueries: [DataSourcesDocument],
  });

  const disconnect = () =>
    deleteDataSource({
      variables: {
        dataSourceId: id,
      },
    }).then(() => {
      refetch([GET_AVAILABLE_FILTERS]);
      navigate(CLOUD_ACCOUNTS);
    });

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
            capabilities: missingCapabilities,
          };
          createSurvey(DATASOURCE_SURVEY_TYPES.DISCONNECT_LAST_DATA_SOURCE, data).then(disconnect);
        } else {
          disconnect();
        }
      }}
    />
  );
};

export default DisconnectCloudAccountContainer;
