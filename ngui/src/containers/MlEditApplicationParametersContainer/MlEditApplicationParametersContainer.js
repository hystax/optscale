import React from "react";
import PropTypes from "prop-types";
import { useParams } from "react-router-dom";
import MlEditApplicationParameters from "components/MlEditApplicationParameters";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlApplicationsService from "services/MlApplicationsService";
import { getParameters as getDemoParameters } from "utils/mlDemoData/parameters";

const DemoContainer = ({ getParameters }) => {
  const onAttachChange = () => {};

  return <MlEditApplicationParameters parameters={getParameters(getDemoParameters())} onAttachChange={onAttachChange} />;
};

const Container = ({ getParameters }) => {
  const { modelId: applicationId } = useParams();
  const { useUpdateApplication, useGetGlobalParameters } = MlApplicationsService();

  const { isLoading: isGetGlobalParametersLoading, parameters: globalParameters } = useGetGlobalParameters();
  const { onUpdate, isLoading: isUpdateLoading } = useUpdateApplication();

  const onAttachChange = (formData) => {
    onUpdate(applicationId, formData);
  };

  return (
    <MlEditApplicationParameters
      parameters={getParameters(globalParameters)}
      onAttachChange={onAttachChange}
      isLoading={isGetGlobalParametersLoading}
      isUpdateLoading={isUpdateLoading}
    />
  );
};

const MlEditApplicationParametersContainer = ({ applicationParameters }) => {
  const { isDemo } = useOrganizationInfo();

  const getParameters = (globalParameters) => {
    const parameters = globalParameters.map((globalParameter) => {
      const isAttached = !!applicationParameters.find(
        (applicationParameter) => applicationParameter.name === globalParameter.name
      );

      return {
        is_attached: isAttached,
        ...globalParameter
      };
    });

    return parameters;
  };

  return isDemo ? <DemoContainer getParameters={getParameters} /> : <Container getParameters={getParameters} />;
};

MlEditApplicationParametersContainer.propTypes = {
  applicationParameters: PropTypes.array.isRequired
};

export default MlEditApplicationParametersContainer;
