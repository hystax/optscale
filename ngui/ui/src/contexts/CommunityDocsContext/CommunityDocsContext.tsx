import { createContext } from "react";

type CommunityDocsContextType = {
  isCommunityDocsOpened: boolean;
  toggleCommunityDocs: () => void;
  openCommunityDocs: () => void;
  closeCommunityDocs: () => void;
};
export default createContext({
  isCommunityDocsOpened: false,
  toggleCommunityDocs: () => {},
  openCommunityDocs: () => {},
  closeCommunityDocs: () => {},
} as CommunityDocsContextType);
