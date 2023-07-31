import { GET_DATA_SOURCES } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { isEmpty } from "utils/arrays";

export const useShouldRenderConnectCloudAccountMock = (cloudAccountType) => {
  const { apiData: { cloudAccounts = [] } = {} } = useApiData(GET_DATA_SOURCES);
  return cloudAccountType
    ? cloudAccounts.findIndex((cloudAccount) => cloudAccount.type === cloudAccountType) === -1
    : isEmpty(cloudAccounts);
};
