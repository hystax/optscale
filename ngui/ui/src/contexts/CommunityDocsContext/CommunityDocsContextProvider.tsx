import { ReactNode } from "react";
import { useToggle } from "hooks/useToggle";
import CommunityDocsContext from "./CommunityDocsContext";

const CommunityDocsContextProvider = ({ children }: { children: ReactNode }) => {
  const [isCommunityDocsOpened, setIsCommunityDocsOpened] = useToggle(false);

  return (
    <CommunityDocsContext.Provider value={{ isCommunityDocsOpened, setIsCommunityDocsOpened }}>
      {children}
    </CommunityDocsContext.Provider>
  );
};

export default CommunityDocsContextProvider;
