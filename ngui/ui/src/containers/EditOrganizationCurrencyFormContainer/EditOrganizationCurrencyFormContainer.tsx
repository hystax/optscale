import { useDispatch } from "react-redux";
import { updateOrganization } from "api";
import { UPDATE_ORGANIZATION } from "api/restapi/actionTypes";
import EditOrganizationCurrencyForm from "components/forms/EditOrganizationCurrencyForm";
import { FormValues } from "components/forms/EditOrganizationCurrencyForm/types";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

const EditOrganizationCurrencyFormContainer = ({ onCancel }) => {
  const dispatch = useDispatch();

  const { isLoading } = useApiState(UPDATE_ORGANIZATION);

  const { currency, organizationId } = useOrganizationInfo();

  const onSubmit = (formData: FormValues) => {
    // There is no need to handle edit mode close since organization will be re-requested after editing
    // and backdrop loader for the entire page will be rendered => edit form will be automatically unmounted
    dispatch(updateOrganization(organizationId, { currency: formData.currency }));
  };

  return (
    <EditOrganizationCurrencyForm defaultCurrency={currency} onSubmit={onSubmit} onCancel={onCancel} isLoading={isLoading} />
  );
};

export default EditOrganizationCurrencyFormContainer;
