import { useContext } from "react";
import { SideModalManagerContext } from "contexts/SideModalManagerContext";

export const useOpenSideModal = () => useContext(SideModalManagerContext);
