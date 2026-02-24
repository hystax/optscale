import CreateOrganizationForm from "components/forms/CreateOrganizationForm";
import { FormValues } from "components/forms/CreateOrganizationForm/types";
import { useCreateOrganizationMutation, useOrganizationsLazyQuery } from "graphql/__generated__/hooks/restapi";

type CreateOrganizationContainerProps = {
  onSuccess: (id: string) => void;
  closeSideModal: () => void;
};

const CreateOrganizationContainer = ({ onSuccess, closeSideModal }: CreateOrganizationContainerProps) => {
  const [createOrganization, { loading: createOrganizationLoading }] = useCreateOrganizationMutation();

  const [getOrganizations, { loading: isOrganizationsLoading }] = useOrganizationsLazyQuery({
    fetchPolicy: "network-only",
  });

  const isLoading = createOrganizationLoading || isOrganizationsLoading;

  const onSubmit = async (formData: FormValues) => {
    const {
      data: {
        createOrganization: { id: organizationId },
      },
    } = await createOrganization({
      variables: {
        organizationName: formData.name,
      },
    });

    await getOrganizations();

    onSuccess(organizationId);
    closeSideModal();
  };

  return <CreateOrganizationForm onCancel={closeSideModal} onSubmit={onSubmit} isLoading={isLoading} />;
};

export default CreateOrganizationContainer;
