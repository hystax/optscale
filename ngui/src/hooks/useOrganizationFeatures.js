import { GET_ORGANIZATION_FEATURES } from "api/restapi/actionTypes";
import { parseJSON } from "utils/strings";
import { useApiData } from "./useApiData";

export const useOrganizationFeatures = () => {
  const {
    apiData: { value: features = "{}" }
  } = useApiData(GET_ORGANIZATION_FEATURES, {});

  return parseJSON(features);
};
