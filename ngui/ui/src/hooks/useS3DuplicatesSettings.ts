import OrganizationOptionsService from "services/OrganizationOptionsService";
import { parseJSON } from "utils/strings";

export const useS3DuplicatesSettings = () => {
  const { useGetS3DuplicatesOrganizationSettings } = OrganizationOptionsService();

  const {
    isLoading,
    options: { value = {} }
  } = useGetS3DuplicatesOrganizationSettings();

  const { thresholds: { requiring_attention: requiringAttention = 50, critical = 200 } = {} } = parseJSON(value);

  return {
    isLoading,
    settings: {
      thresholds: { requiringAttention, critical }
    }
  };
};
