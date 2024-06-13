import { useDispatch } from "react-redux";
import { updateOrganization } from "api";
import { UPDATE_ORGANIZATION } from "api/restapi/actionTypes";
import EditOrganizationForm from "components/forms/EditOrganizationForm";
import { FormValues } from "components/forms/EditOrganizationForm/types";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

type EditOrganizationFormContainerProps = {
  onCancel: () => void;
};

const EditOrganizationFormContainer = ({ onCancel }: EditOrganizationFormContainerProps) => {
  const dispatch = useDispatch();

  const { isLoading } = useApiState(UPDATE_ORGANIZATION);

  const { name: currentOrganizationName, organizationId } = useOrganizationInfo();

  const onSubmit = ({ organizationName }: FormValues) => {
    // There is no need to handle edit mode close since organization will be re-requested after deletion
    // and backdrop loader for the entire page will be rendered => edit form will be automatically unmounted
    dispatch(updateOrganization(organizationId, { name: organizationName }));
  };

  return (
    <EditOrganizationForm
      currentOrganizationName={currentOrganizationName}
      onSubmit={onSubmit}
      onCancel={onCancel}
      isLoading={isLoading}
    />
  );
};

export default EditOrganizationFormContainer;
