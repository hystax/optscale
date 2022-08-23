import { useContext } from "react";
import { PageMockupContext } from "contexts/PageMockupContext";

export const useInScopeOfPageMockup = () => {
  const { isInScopeOfPageMockup } = useContext(PageMockupContext);

  return isInScopeOfPageMockup;
};
