import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { createDataSource } from "api";
import { CREATE_DATA_SOURCE } from "api/restapi/actionTypes";
import ConnectCloudAccount from "components/ConnectCloudAccount";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { CLOUD_ACCOUNTS } from "urls";
import { trackEvent, GA_EVENT_CATEGORIES } from "utils/analytics";
import { isError } from "utils/api";

const ConnectCloudAccountContainer = () => {
  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(CREATE_DATA_SOURCE);

  const navigate = useNavigate();
  const dispatch = useDispatch();

  const redirectToCloudsOverview = () => navigate(CLOUD_ACCOUNTS);

  const onSubmit = (params) => {
    dispatch((_, getState) => {
      dispatch(createDataSource(organizationId, params)).then(() => {
        if (!isError(CREATE_DATA_SOURCE, getState())) {
          redirectToCloudsOverview();
        }
      });
    });
    trackEvent({ category: GA_EVENT_CATEGORIES.DATA_SOURCE, action: "Try connect", label: params.type });
  };

  return <ConnectCloudAccount isLoading={isLoading} onSubmit={onSubmit} onCancel={redirectToCloudsOverview} />;
};

export default ConnectCloudAccountContainer;
