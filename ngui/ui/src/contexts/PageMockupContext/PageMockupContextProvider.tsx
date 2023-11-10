import PageMockupContext from "./PageMockupContext";

const PageMockupContextProvider = ({ children }) => (
  <PageMockupContext.Provider value={{ isInScopeOfPageMockup: true }}>{children}</PageMockupContext.Provider>
);

export default PageMockupContextProvider;
