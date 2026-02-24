import EditOrganizationCurrencyForm from "components/forms/EditOrganizationCurrencyForm";
import { FormValues } from "components/forms/EditOrganizationCurrencyForm/types";
import { useUpdateOrganizationMutation } from "graphql/__generated__/hooks/restapi";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

type EditOrganizationCurrencyFormContainerProps = {
  onCancel: () => void;
  onSuccess: () => void;
};

const EditOrganizationCurrencyFormContainer = ({ onCancel, onSuccess }: EditOrganizationCurrencyFormContainerProps) => {
  const { currency, organizationId } = useOrganizationInfo();

  const [updateOrganization, { loading }] = useUpdateOrganizationMutation();

  const onSubmit = (formData: FormValues) => {
    updateOrganization({
      variables: {
        organizationId,
        params: {
          currency: formData.currency,
        },
      },
    }).then(onSuccess);
  };

  return (
    <EditOrganizationCurrencyForm defaultCurrency={currency} onSubmit={onSubmit} onCancel={onCancel} isLoading={loading} />
  );
};

export default EditOrganizationCurrencyFormContainer;
