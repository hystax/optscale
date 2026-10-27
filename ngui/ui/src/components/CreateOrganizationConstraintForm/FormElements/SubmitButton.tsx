import { CREATE_ORGANIZATION_CONSTRAINT } from "api/restapi/actionTypes";
import ButtonLoader from "components/ButtonLoader";
import { useApiState } from "hooks/useApiState";
import { useOrganizationActionRestrictions } from "hooks/useOrganizationActionRestrictions";
import AvailableFiltersService from "services/AvailableFiltersService";

const SubmitButton = () => {
  const { isRestricted, restrictionReasonMessage } = useOrganizationActionRestrictions();

  const { useIsLoading: useIsAvailableFiltersLoading } = AvailableFiltersService();

  const isAvailableFiltersLoading = useIsAvailableFiltersLoading();

  const { isLoading: isCreateOrganizationConstraintLoading } = useApiState(CREATE_ORGANIZATION_CONSTRAINT);

  return (
    <ButtonLoader
      variant="contained"
      messageId="save"
      color="primary"
      type="submit"
      isLoading={isAvailableFiltersLoading || isCreateOrganizationConstraintLoading}
      disabled={isRestricted}
      tooltip={{
        show: isRestricted,
        value: restrictionReasonMessage,
      }}
      dataTestId="btn_create"
    />
  );
};

export default SubmitButton;
