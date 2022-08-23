import { GET_CLOUD_ACCOUNTS } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { isEmpty } from "utils/arrays";

export const useShouldRenderConnectCloudAccountMock = (cloudAccountType) => {
  const { apiData: { cloudAccounts = [] } = {} } = useApiData(GET_CLOUD_ACCOUNTS);
  return cloudAccountType
    ? cloudAccounts.findIndex((cloudAccount) => cloudAccount.type === cloudAccountType) === -1
    : isEmpty(cloudAccounts);
};
