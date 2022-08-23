import React from "react";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { createCloudAccount } from "api";
import { CREATE_CLOUD_ACCOUNT } from "api/restapi/actionTypes";
import { GAEvent, GA_EVENT_CATEGORIES } from "components/ActivityListener";
import ConnectCloudAccount from "components/ConnectCloudAccount";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { CLOUD_ACCOUNTS } from "urls";
import { isError } from "utils/api";

const ConnectCloudAccountContainer = () => {
  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(CREATE_CLOUD_ACCOUNT);

  const navigate = useNavigate();
  const dispatch = useDispatch();

  const redirectToCloudsOverview = () => navigate(CLOUD_ACCOUNTS);

  const onSubmit = (params) => {
    dispatch((_, getState) => {
      dispatch(createCloudAccount(organizationId, params)).then(() => {
        if (!isError(CREATE_CLOUD_ACCOUNT, getState())) {
          redirectToCloudsOverview();
        }
      });
    });
    GAEvent({ category: GA_EVENT_CATEGORIES.DATA_SOURCE, action: "Try connect", label: params.type });
  };

  return <ConnectCloudAccount isLoading={isLoading} onSubmit={onSubmit} onCancel={redirectToCloudsOverview} />;
};

export default ConnectCloudAccountContainer;
