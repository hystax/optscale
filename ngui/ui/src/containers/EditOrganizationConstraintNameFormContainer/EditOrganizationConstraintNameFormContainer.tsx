import EditOrganizationConstraintNameForm from "components/forms/EditOrganizationConstraintNameForm";
import { FormValues } from "components/forms/EditOrganizationConstraintNameForm/types";
import OrganizationConstraintsService from "services/OrganizationConstraintsService";

const EditOrganizationConstraintNameFormContainer = ({ id, name, onCancel, onSuccess }) => {
  const { useUpdate } = OrganizationConstraintsService();
  const { isLoading, update } = useUpdate();

  const onSubmit = (formData: FormValues) =>
    update({
      id,
      params: {
        name: formData.name
      },
      onSuccess
    });

  return (
    <EditOrganizationConstraintNameForm defaultName={name} onCancel={onCancel} onSubmit={onSubmit} isLoading={isLoading} />
  );
};

export default EditOrganizationConstraintNameFormContainer;
