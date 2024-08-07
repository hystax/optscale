import { type ReactNode } from "react";
import { useIsOptScaleModeEnabled } from "hooks/useIsOptScaleModeEnabled";
import { OPTSCALE_MODE } from "utils/constants";

type ModeWrapperProps = {
  children: ReactNode;
  mode: (typeof OPTSCALE_MODE)[keyof typeof OPTSCALE_MODE] | undefined;
};

const ModeWrapper = ({ children, mode }: ModeWrapperProps) => {
  const shouldShowChildren = useIsOptScaleModeEnabled(mode);

  return shouldShowChildren ? children : null;
};

export default ModeWrapper;
