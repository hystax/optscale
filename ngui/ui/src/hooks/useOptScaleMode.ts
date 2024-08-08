import OrganizationOptionsService from "services/OrganizationOptionsService";
import { OPTSCALE_MODE_OPTION } from "utils/constants";

export const useOptScaleMode = () => {
  const { useGetOptscaleMode } = OrganizationOptionsService();

  const {
    // Intentionally ignore loading state to update the state 'silently'
    option: { value: optScaleMode }
  } = useGetOptscaleMode(OPTSCALE_MODE_OPTION);

  return optScaleMode;
};
