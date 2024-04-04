import { useEffect, useState, type ReactNode } from "react";
import OrganizationOptionsService from "services/OrganizationOptionsService";
import { OPTSCALE_MODE_OPTION, OPTSCALE_MODE } from "utils/constants";

type ModeWrapperProps = {
  children: ReactNode;
  mode: (typeof OPTSCALE_MODE)[keyof typeof OPTSCALE_MODE] | undefined;
};

const ModeWrapper = ({ children, mode }: ModeWrapperProps) => {
  const [shouldShowChildren, setShouldShowChildren] = useState(false);

  const { useGetOptscaleMode } = OrganizationOptionsService();

  const {
    // Intentionally ignore loading state to update the menu 'silently'
    option: { value }
  } = useGetOptscaleMode(OPTSCALE_MODE_OPTION);

  useEffect(() => {
    // This handles 2 cases, in both of them we need to display children.
    // 1. If there is no mode explicitly defined for a component
    // 2. if there is no OPTSCALE_MODE_OPTION defined at all
    setShouldShowChildren(value?.[mode] ?? true);
  }, [value, mode]);

  return shouldShowChildren ? children : null;
};

export default ModeWrapper;
