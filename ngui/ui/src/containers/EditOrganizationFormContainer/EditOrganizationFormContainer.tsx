import EditOrganizationForm from "components/forms/EditOrganizationForm";
import { FormValues } from "components/forms/EditOrganizationForm/types";
import { useUpdateOrganizationMutation } from "graphql/__generated__/hooks/restapi";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

type EditOrganizationFormContainerProps = {
  onCancel: () => void;
  onSuccess: () => void;
};

const EditOrganizationFormContainer = ({ onCancel, onSuccess }: EditOrganizationFormContainerProps) => {
  const { name: currentOrganizationName, organizationId } = useOrganizationInfo();

  const [updateOrganization, { loading }] = useUpdateOrganizationMutation();

  const onSubmit = ({ organizationName }: FormValues) => {
    updateOrganization({
      variables: {
        organizationId,
        params: {
          name: organizationName,
        },
      },
    }).then(onSuccess);
  };

  return (
    <EditOrganizationForm
      currentOrganizationName={currentOrganizationName}
      onSubmit={onSubmit}
      onCancel={onCancel}
      isLoading={loading}
    />
  );
};

export default EditOrganizationFormContainer;
