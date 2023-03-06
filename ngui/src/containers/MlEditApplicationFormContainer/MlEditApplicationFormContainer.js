import React from "react";
import { useNavigate, useParams } from "react-router-dom";
import MlEditApplicationForm from "components/MlEditApplicationForm";
import EmployeesService from "services/EmployeesService";
import MlApplicationsService from "services/MlApplicationsService";
import { getMlDetailsUrl } from "urls";

const MlEditApplicationFormContainer = ({ application }) => {
  const { modelId } = useParams();
  const navigate = useNavigate();

  const { useUpdateApplication } = MlApplicationsService();
  const { onUpdate, isLoading } = useUpdateApplication();

  const { useGet: useGetEmployees } = EmployeesService();
  const { isLoading: isGetEmployeesLoading, employees } = useGetEmployees();

  const redirectToApplicationDetails = () => navigate(getMlDetailsUrl(modelId));

  const onSubmit = (formData) => {
    onUpdate(modelId, {
      name: formData.name,
      owner_id: formData.ownerId
    }).then(() => {
      redirectToApplicationDetails();
    });
  };

  const onCancel = () => redirectToApplicationDetails();

  return (
    <MlEditApplicationForm
      application={application}
      onSubmit={onSubmit}
      onCancel={onCancel}
      employees={employees}
      isGetEmployeesLoading={isGetEmployeesLoading}
      isSubmitLoading={isLoading}
    />
  );
};

// MlEditApplicationFormContainer.propTypes = {
// };

export default MlEditApplicationFormContainer;
