import React from "react";
import { CREATE_ORGANIZATION_CONSTRAINT } from "api/restapi/actionTypes";
import ButtonLoader from "components/ButtonLoader";
import { useApiState } from "hooks/useApiState";
import AvailableFiltersService from "services/AvailableFiltersService";

const SubmitButton = () => {
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
      dataTestId="btn_create"
    />
  );
};

export default SubmitButton;
