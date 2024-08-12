import { createContext } from "react";

type CommunityDocsContextType = {
  isCommunityDocsOpened: boolean;
  setIsCommunityDocsOpened: () => void;
};
export default createContext({
  isCommunityDocsOpened: false,
  setIsCommunityDocsOpened: () => {},
  closeTips: () => {}
} as CommunityDocsContextType);
