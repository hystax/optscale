import KubernetesIntegration from "components/KubernetesIntegration";
import BaseSideModal from "./BaseSideModal";

class KubernetesIntegrationModal extends BaseSideModal {
  headerProps = {
    messageId: "kubernetesCostMetricCollectorIntegrationTitle",
    color: "primary",
    dataTestIds: {
      title: "lbl_kubernetes_integration",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_kubernetes_integration";

  get content() {
    return <KubernetesIntegration dataSourceId={this.payload?.dataSourceId} user={this.payload?.user} />;
  }
}

export default KubernetesIntegrationModal;
