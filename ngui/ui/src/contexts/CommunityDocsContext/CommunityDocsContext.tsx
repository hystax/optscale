import React from "react";

type CommunityDocsContextType = {
  isOpened: boolean;
  openTips: () => void;
  closeTips: () => void;
  allRoutesPatterns: readonly string[];
};
export default React.createContext({
  isOpened: false,
  openTips: () => {},
  closeTips: () => {},
  allRoutesPatterns: []
} as CommunityDocsContextType);
