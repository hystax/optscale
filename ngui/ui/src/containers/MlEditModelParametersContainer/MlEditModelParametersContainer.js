import React from "react";
import PropTypes from "prop-types";
import { useParams } from "react-router-dom";
import MlEditModelParameters from "components/MlEditModelParameters";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlModelsService from "services/MlModelsService";
import { getParameters as getDemoParameters } from "utils/mlDemoData/parameters";

const DemoContainer = ({ getParameters }) => {
  const onAttachChange = () => {};

  return <MlEditModelParameters parameters={getParameters(getDemoParameters())} onAttachChange={onAttachChange} />;
};

const Container = ({ getParameters }) => {
  const { modelId } = useParams();
  const { useUpdateModel, useGetGlobalParameters } = MlModelsService();

  const { isLoading: isGetGlobalParametersLoading, parameters: globalParameters } = useGetGlobalParameters();
  const { onUpdate, isLoading: isUpdateLoading } = useUpdateModel();

  const onAttachChange = (formData) => {
    onUpdate(modelId, formData);
  };

  return (
    <MlEditModelParameters
      parameters={getParameters(globalParameters)}
      onAttachChange={onAttachChange}
      isLoading={isGetGlobalParametersLoading}
      isUpdateLoading={isUpdateLoading}
    />
  );
};

const MlEditModelParametersContainer = ({ modelParameters }) => {
  const { isDemo } = useOrganizationInfo();

  const getParameters = (globalParameters) => {
    const parameters = globalParameters.map((globalParameter) => {
      const isAttached = !!modelParameters.find((modelParameter) => modelParameter.key === globalParameter.key);

      return {
        is_attached: isAttached,
        ...globalParameter
      };
    });

    return parameters;
  };

  return isDemo ? <DemoContainer getParameters={getParameters} /> : <Container getParameters={getParameters} />;
};

MlEditModelParametersContainer.propTypes = {
  modelParameters: PropTypes.array.isRequired
};

export default MlEditModelParametersContainer;
