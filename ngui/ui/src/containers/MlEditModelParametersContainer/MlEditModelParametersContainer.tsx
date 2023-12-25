import { useParams } from "react-router-dom";
import MlEditModelParameters from "components/MlEditModelParameters";
import MlModelsService from "services/MlModelsService";

const MlEditModelParametersContainer = ({ modelParameters }) => {
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

  const { taskId } = useParams();
  const { useUpdateModel, useGetGlobalParameters } = MlModelsService();

  const { isLoading: isGetGlobalParametersLoading, parameters: globalParameters } = useGetGlobalParameters();
  const { onUpdate, isLoading: isUpdateLoading } = useUpdateModel();

  const onAttachChange = (formData) => {
    onUpdate(taskId, formData);
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

export default MlEditModelParametersContainer;
