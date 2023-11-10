import SideModalManagerContext from "./SideModalManagerContext";

const SideModalManagerContextProvider = ({ children, openSideModal }) => (
  <SideModalManagerContext.Provider value={openSideModal}>{children}</SideModalManagerContext.Provider>
);

export default SideModalManagerContextProvider;
