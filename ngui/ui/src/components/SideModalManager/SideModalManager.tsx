import { useEffect, useState, useCallback } from "react";
import { Box } from "@mui/material";
import { useLocation } from "react-router-dom";
import ErrorBoundary from "components/ErrorBoundary";
import SideModal from "components/SideModal";
import { SideModalManagerContextProvider } from "contexts/SideModalManagerContext";

const SideModalManager = ({ children }) => {
  const [currentSideModalInstance, setCurrentSideModalInstance] = useState(null);
  const [isOpen, setIsOpen] = useState(false);
  const close = useCallback(() => {
    setIsOpen(false);
  }, []);

  const openSideModal = useCallback(
    (SideModalClass, payload = {}) => {
      setCurrentSideModalInstance((prevInstance) => {
        // if same side modal — just updating payload
        if (prevInstance instanceof SideModalClass) {
          prevInstance.initialize(payload);
          return prevInstance;
        }

        // if different sidemodal — trying to destroy previous
        if (prevInstance) {
          prevInstance.destroy();
        }

        // setting new sidemodal with payload and close handler
        return new SideModalClass(payload, close);
      });
      setIsOpen(true);
    },
    [close]
  );

  // close sidemodal if path changed
  const { pathname } = useLocation();
  useEffect(close, [close, pathname]);

  // rendering its content
  const { content = null, headerProps = {}, dataTestId, contentPadding } = currentSideModalInstance ?? {};

  const isSideModalOpen = isOpen && !!currentSideModalInstance;

  return (
    <SideModalManagerContextProvider openSideModal={openSideModal}>
      {children}
      <SideModal isOpen={isSideModalOpen} headerProps={headerProps} onClose={close} dataTestId={dataTestId}>
        <Box pl={contentPadding} pr={contentPadding}>
          <ErrorBoundary>{content}</ErrorBoundary>
        </Box>
      </SideModal>
    </SideModalManagerContextProvider>
  );
};

export default SideModalManager;
