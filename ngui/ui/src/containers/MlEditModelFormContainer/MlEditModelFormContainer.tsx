import { useNavigate, useParams } from "react-router-dom";
import MlEditModelForm from "components/MlEditModelForm";
import EmployeesService from "services/EmployeesService";
import MlModelsService from "services/MlModelsService";
import { getMlModelDetailsUrl } from "urls";
import { ML_MODEL_DETAILS_TAB_NAME } from "utils/constants";
import { getQueryParams } from "utils/network";

const MlEditModelFormContainer = ({ model }) => {
  const { taskId } = useParams();
  const navigate = useNavigate();

  const { useUpdateModel } = MlModelsService();
  const { onUpdate, isLoading } = useUpdateModel();

  const { useGet: useGetEmployees } = EmployeesService();
  const { isLoading: isGetEmployeesLoading, employees } = useGetEmployees();

  const redirectToModelDetails = () => {
    const { [ML_MODEL_DETAILS_TAB_NAME]: taskDetailsTab } = getQueryParams();

    return navigate(`${getMlModelDetailsUrl(taskId)}?${ML_MODEL_DETAILS_TAB_NAME}=${taskDetailsTab}`);
  };

  const onSubmit = (formData) => {
    onUpdate(taskId, formData).then(() => {
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
