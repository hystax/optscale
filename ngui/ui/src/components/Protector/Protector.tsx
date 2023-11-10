import Error from "components/Error";
import { useIsAllowed } from "hooks/useAllowedActions";

const Protector = ({ children, allowedActions = [] }) => {
  const shouldRenderChildren = useIsAllowed({ requiredActions: allowedActions });

  return shouldRenderChildren ? children : <Error messageId="forbidden" />;
};

export default Protector;
