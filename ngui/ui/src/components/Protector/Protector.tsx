import { type ReactNode } from "react";
import Error from "components/Error";
import { useIsAllowed } from "hooks/useAllowedActions";

type ProtectorProps = {
  children: ReactNode;
  allowedActions: string[];
};

const Protector = ({ children, allowedActions = [] }: ProtectorProps) => {
  const shouldRenderChildren = useIsAllowed({ requiredActions: allowedActions });

  return shouldRenderChildren ? children : <Error messageId="forbidden" />;
};

export default Protector;
