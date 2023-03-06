import React from "react";
import ProfilingIntegrationContainer from "containers/ProfilingIntegrationContainer";
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

  // eslint-disable-next-line class-methods-use-this
  get content() {
    return <ProfilingIntegrationContainer />;
  }
}

export default ProfilingIntegrationModal;
