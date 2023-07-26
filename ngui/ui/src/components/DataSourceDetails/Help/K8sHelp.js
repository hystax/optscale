import React from "react";
import Link from "@mui/material/Link";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import { GITHUB_HYSTAX_K8S_COST_METRICS_COLLECTOR } from "urls";

const K8sHelp = () => (
  <InlineSeverityAlert
    messageId="connectKubernetesTip"
    messageValues={{
      kubernetesConnectGuide: (
        <Link data-test-id="link_guide" href={GITHUB_HYSTAX_K8S_COST_METRICS_COLLECTOR} target="_blank" rel="noopener">
          {GITHUB_HYSTAX_K8S_COST_METRICS_COLLECTOR}
        </Link>
      )
    }}
  />
);

export default K8sHelp;
