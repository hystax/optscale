import { createContext } from "react";

type CommunityDocsContextType = {
  isCommunityDocsOpened: boolean;
  setIsCommunityDocsOpened: () => void;
  allRoutesPatterns: readonly string[];
};
export default createContext({
  isCommunityDocsOpened: false,
  setIsCommunityDocsOpened: () => {},
  closeTips: () => {},
  allRoutesPatterns: []
} as CommunityDocsContextType);
