import { useEffect, useState } from "react";
import { useOptScaleMode } from "./useOptScaleMode";

export const useIsOptScaleModeEnabled = (mode) => {
  const [isEnabled, setIsEnabled] = useState(false);

  const value = useOptScaleMode();

  useEffect(() => {
    // This handles 2 cases, in both of them we need to display children.
    // 1. If there is no mode explicitly defined for a component
    // 2. if there is no OPTSCALE_MODE_OPTION defined at all
    setIsEnabled(value?.[mode] ?? true);
  }, [value, mode]);

  return isEnabled;
};
