import { useNavigate, useParams } from "react-router-dom";
import MlEditModelForm from "components/MlEditModelForm";
import EmployeesService from "services/EmployeesService";
import MlModelsService from "services/MlModelsService";
import { getMlModelDetailsUrl } from "urls";

const MlEditModelFormContainer = ({ model }) => {
  const { modelId } = useParams();
  const navigate = useNavigate();

  const { useUpdateModel } = MlModelsService();
  const { onUpdate, isLoading } = useUpdateModel();

  const { useGet: useGetEmployees } = EmployeesService();
  const { isLoading: isGetEmployeesLoading, employees } = useGetEmployees();

  const redirectToModelDetails = () => navigate(getMlModelDetailsUrl(modelId));

  const onSubmit = (formData) => {
    onUpdate(modelId, {
      name: formData.name,
      owner_id: formData.ownerId
    }).then(() => {
      redirectToModelDetails();
    });
  };

  const onCancel = () => redirectToModelDetails();

  return (
    <MlEditModelForm
      model={model}
      onSubmit={onSubmit}
      onCancel={onCancel}
      employees={employees}
      isGetEmployeesLoading={isGetEmployeesLoading}
      isSubmitLoading={isLoading}
    />
  );
};

export default MlEditModelFormContainer;
