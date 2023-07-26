import React from "react";
import CreateOrganizationForm from "components/CreateOrganizationForm";
import OrganizationsService from "services/OrganizationsService";

const CreateOrganizationContainer = ({ onSuccess, closeSideModal }) => {
  const { useCreate, useGet } = OrganizationsService();

  const { onCreate, isLoading: isCreateLoading } = useCreate();
  const { getOrganizations, isLoading: isGetLoading } = useGet();

  const isLoading = isCreateLoading || isGetLoading;

  const onSubmit = async (name) => {
    const { id } = await onCreate(name);
    await getOrganizations();
    onSuccess(id);
    closeSideModal();
  };

  return <CreateOrganizationForm onCancel={closeSideModal} onSubmit={onSubmit} isLoading={isLoading} />;
};

export default CreateOrganizationContainer;
