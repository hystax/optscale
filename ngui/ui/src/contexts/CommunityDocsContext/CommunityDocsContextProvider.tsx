import { ReactNode } from "react";
import { useToggle } from "hooks/useToggle";
import { ALL_ROUTES_PATTERNS } from "utils/routes";
import CommunityDocsContext from "./CommunityDocsContext";

const CommunityDocsContextProvider = ({ children }: { children: ReactNode }) => {
  const [isCommunityDocsOpened, setIsCommunityDocsOpened] = useToggle(false);

  return (
    <CommunityDocsContext.Provider
      value={{ isCommunityDocsOpened, setIsCommunityDocsOpened, allRoutesPatterns: ALL_ROUTES_PATTERNS }}
    >
      {children}
    </CommunityDocsContext.Provider>
  );
};

export default CommunityDocsContextProvider;
