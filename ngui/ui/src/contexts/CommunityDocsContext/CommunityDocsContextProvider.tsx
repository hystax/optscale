import { useCallback, useState, ReactNode } from "react";
import { ALL_ROUTES_PATTERNS } from "utils/routes";
import CommunityDocsContext from "./CommunityDocsContext";

const CommunityDocsContextProvider = ({ children }: { children: ReactNode }) => {
  const [isOpened, setIsOpened] = useState(false);
  const openTips = useCallback(() => setIsOpened(true), []);
  const closeTips = useCallback(() => setIsOpened(false), []);

  return (
    <CommunityDocsContext.Provider value={{ isOpened, openTips, closeTips, allRoutesPatterns: ALL_ROUTES_PATTERNS }}>
      {children}
    </CommunityDocsContext.Provider>
  );
};

export default CommunityDocsContextProvider;
