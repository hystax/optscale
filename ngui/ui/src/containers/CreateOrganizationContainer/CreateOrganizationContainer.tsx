import CreateOrganizationForm from "components/forms/CreateOrganizationForm";
import { FormValues } from "components/forms/CreateOrganizationForm/types";
import OrganizationsService from "services/OrganizationsService";

const CreateOrganizationContainer = ({ onSuccess, closeSideModal }) => {
  const { useCreate, useGet } = OrganizationsService();

  const { onCreate, isLoading: isCreateLoading } = useCreate();
  const { getOrganizations, isLoading: isGetLoading } = useGet();

  const isLoading = isCreateLoading || isGetLoading;

  const onSubmit = async (formData: FormValues) => {
    const { id } = await onCreate(formData.name);
    await getOrganizations();
    onSuccess(id);
    closeSideModal();
  };

  return <CreateOrganizationForm onCancel={closeSideModal} onSubmit={onSubmit} isLoading={isLoading} />;
};

export default CreateOrganizationContainer;
