import { GET_ORGANIZATION_THEME_SETTINGS } from "api/restapi/actionTypes";
import { parseJSON } from "utils/strings";
import { useApiData } from "./useApiData";

export const useOrganizationThemeSettings = () => {
  const {
    apiData: { value: themeSettings = "{}" }
  } = useApiData(GET_ORGANIZATION_THEME_SETTINGS, {});

  return parseJSON(themeSettings);
};
