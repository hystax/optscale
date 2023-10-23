import React from "react";
import PropTypes from "prop-types";
import { FormProvider, useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import DisconnectCloudAccount from "components/DisconnectCloudAccount";
import { FIELD_REASON, FIELD_CAPABILITIES, FIELD_OTHER } from "components/DisconnectCloudAccount/FormElements";
import DataSourcesService from "services/DataSourcesService";
import SurveyService, { SURVEY_TYPES } from "services/SurveyService";
import { CLOUD_ACCOUNTS } from "urls";

const DisconnectCloudAccountContainer = ({ id, type, parentId, onCancel }) => {
  const navigate = useNavigate();

  const { createSurvey, isLoading: isCreateSurveyLoading } = SurveyService().useCreateSurvey();
  const { disconnectDataSource, isLoading } = DataSourcesService().useDisconnectDataSource();
  const disconnectAndRedirect = () => disconnectDataSource(id).then(() => navigate(CLOUD_ACCOUNTS));

  const isLastDataSource = DataSourcesService().useIsLastDataSource();

  const methods = useForm({ defaultValues: { [FIELD_REASON]: "", [FIELD_CAPABILITIES]: "", [FIELD_OTHER]: "" } });
  const { handleSubmit } = methods;

  const onSubmitHandler = handleSubmit((formData) => {
    const isReasonSelected = !!formData[FIELD_REASON];
    const isCapabilitiesAdded = !!formData[FIELD_CAPABILITIES];

    if (isLastDataSource && (isReasonSelected || isCapabilitiesAdded)) {
      createSurvey(SURVEY_TYPES.DISCONNECT_LAST_DATA_SOURCE, formData).then(disconnectAndRedirect);
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
          isLoading={isLoading || isCreateSurveyLoading}
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
