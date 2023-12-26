import React from "react";

type CommunityDocsContextType = {
  isCommunityDocsOpened: boolean;
  setIsCommunityDocsOpened: () => void;
  allRoutesPatterns: readonly string[];
};
export default React.createContext({
  isCommunityDocsOpened: false,
  setIsCommunityDocsOpened: () => {},
  closeTips: () => {},
  allRoutesPatterns: []
} as CommunityDocsContextType);
