import React from "react";
import PropTypes from "prop-types";
import { FormProvider, useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import DisconnectCloudAccount from "components/DisconnectCloudAccount";
import { FIELD_REASON, FIELD_CAPABILITIES, FIELD_OTHER, getReasonValue } from "components/DisconnectCloudAccount/FormElements";
import DataSourcesService, { DATASOURCE_SURVEY_TYPES } from "services/DataSourcesService";
import { CLOUD_ACCOUNTS } from "urls";

const DisconnectCloudAccountContainer = ({ id, type, parentId, onCancel }) => {
  const navigate = useNavigate();

  const { useDisconnectDataSource, useCreateSurvey, useIsLastDataSource } = DataSourcesService();

  const { isLoading: isDisconnectDataSourceLoading, disconnectDataSource } = useDisconnectDataSource();
  const disconnectAndRedirect = () => disconnectDataSource(id).then(() => navigate(CLOUD_ACCOUNTS));

  const { isLoading: isCreateSurveyLoading, createSurvey } = useCreateSurvey();

  const isLastDataSource = useIsLastDataSource();

  const methods = useForm({ defaultValues: { [FIELD_REASON]: "", [FIELD_CAPABILITIES]: "", [FIELD_OTHER]: "" } });
  const { handleSubmit } = methods;

  const onSubmitHandler = handleSubmit((formData) => {
    const reasonKey = formData[FIELD_REASON];
    const isReasonSelected = !!reasonKey;
    const isCapabilitiesAdded = !!formData[FIELD_CAPABILITIES];

    if (isLastDataSource && (isReasonSelected || isCapabilitiesAdded)) {
      const data = {
        ...formData,
        [FIELD_REASON]: getReasonValue(reasonKey)
      };
      createSurvey(DATASOURCE_SURVEY_TYPES.DISCONNECT_LAST_DATA_SOURCE, data).then(disconnectAndRedirect);
    } else {
      disconnectAndRedirect();
    }
  });

  return (
    <FormProvider {...methods}>
      <form data-test-id="disconnect-datasource-form" onSubmit={onSubmitHandler} noValidate>
        <DisconnectCloudAccount
          isLastDataSource={isLastDataSource}
          type={type}
          parentId={parentId}
          onCancel={onCancel}
          isLoading={isDisconnectDataSourceLoading || isCreateSurveyLoading}
        />
      </form>
    </FormProvider>
  );
};

DisconnectCloudAccountContainer.propTypes = {
  id: PropTypes.string.isRequired,
  onCancel: PropTypes.func.isRequired,
  type: PropTypes.string.isRequired,
  parentId: PropTypes.string
};

export default DisconnectCloudAccountContainer;
