import React from "react";
import ProfilingIntegrationContainer from "containers/ProfilingIntegrationContainer";
import { ProfilingIntegrationModalContextProvider } from "contexts/ProfilingIntegrationModalContext";
import BaseSideModal from "./BaseSideModal";

class ProfilingIntegrationModal extends BaseSideModal {
  headerProps = {
    messageId: "profilingIntegrationTitle",
    dataTestIds: {
      title: "lbl_profiling_integration",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_profiling_integration";

  get content() {
    return (
      <ProfilingIntegrationModalContextProvider onClose={this.closeSideModal}>
        <ProfilingIntegrationContainer modelKey={this.payload?.modelKey} />
      </ProfilingIntegrationModalContextProvider>
    );
  }
}

export default ProfilingIntegrationModal;
