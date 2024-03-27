import Link from "@mui/material/Link";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import { KubernetesIntegrationModal } from "components/SideModalManager/SideModals";
import { useOpenSideModal } from "hooks/useOpenSideModal";

type K8sHelpProps = {
  dataSourceId: string;
  user: string;
};

const K8sHelp = ({ dataSourceId, user }: K8sHelpProps) => {
  const openSideModal = useOpenSideModal();

  return (
    <InlineSeverityAlert
      messageId="connectKubernetesTip"
      messageValues={{
        instructionLinkButton: (chunks) => (
          <Link
            component="button"
            sx={{
              verticalAlign: "baseline"
            }}
            onClick={() =>
              openSideModal(KubernetesIntegrationModal, {
                dataSourceId,
                user
              })
            }
          >
            {chunks}
          </Link>
        )
      }}
    />
  );
};

export default K8sHelp;
