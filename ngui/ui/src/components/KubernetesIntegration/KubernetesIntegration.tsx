import { Stack, Typography } from "@mui/material";
import Link from "@mui/material/Link";
import { FormattedMessage } from "react-intl";
import CodeBlock from "components/CodeBlock";
import SubTitle from "components/SubTitle";
import { GITHUB_HYSTAX_K8S_COST_METRICS_COLLECTOR, isProduction } from "urls";
import { SPACING_1 } from "utils/layouts";

type KubernetesIntegrationProps = {
  dataSourceId: string;
  user: string;
};

type SecondStepProps = {
  dataSourceId: string;
  user: string;
};

const FirstStep = () => (
  <>
    <SubTitle fontWeight="bold">
      <FormattedMessage id="kubernetesIntegration.firstStep.title" />
    </SubTitle>
    <CodeBlock text="helm repo add hystax https://hystax.github.io/helm-charts" />
  </>
);

const SecondStep = ({ dataSourceId, user }: SecondStepProps) => (
  <>
    <SubTitle fontWeight="bold">
      <FormattedMessage id="kubernetesIntegration.secondStep.title" />
    </SubTitle>
    <CodeBlock
      text={
        isProduction()
          ? `helm install kube-cost-metrics-collector hystax/kube-cost-metrics-collector \\
--set prometheus.server.dataSourceId=${dataSourceId} \\
--set prometheus.server.username=${user} \\
--set prometheus.server.password=<password_specified_during_data_source_connection> \\
--namespace optscale \\
--create-namespace`
          : `helm install kube-cost-metrics-collector hystax/kube-cost-metrics-collector \\
--set prometheus.server.dataSourceId=${dataSourceId} \\
--set prometheus.server.username=${user} \\
--set prometheus.server.password=<password_specified_during_data_source_connection> \\
--set prometheus.server.remote_write[0].url=https://${window.location.host}/storage/api/v2/write \\
--set prometheus.server.remote_write[0].name=optscale \\
--namespace optscale \\
--create-namespace`
      }
    />
  </>
);

const ThirdStep = () => (
  <>
    <SubTitle fontWeight="bold">
      <FormattedMessage id="kubernetesIntegration.thirdStep.title" />
    </SubTitle>
    <Typography>
      <FormattedMessage id="kubernetesIntegration.thirdStep.waitForMetrics" />
    </Typography>
  </>
);

const KubernetesIntegration = ({ dataSourceId, user }: KubernetesIntegrationProps) => (
  <Stack spacing={SPACING_1}>
    <div>
      <Typography gutterBottom>
        <FormattedMessage id="kubernetesIntegration.installCollectorSoftware" />
      </Typography>
      <Typography gutterBottom>
        <FormattedMessage
          id="kubernetesIntegration.moreDetailsDescriptionLink"
          values={{
            kubernetesConnectGuide: (
              <Link data-test-id="link_guide" href={GITHUB_HYSTAX_K8S_COST_METRICS_COLLECTOR} target="_blank" rel="noopener">
                {GITHUB_HYSTAX_K8S_COST_METRICS_COLLECTOR}
              </Link>
            )
          }}
        />
      </Typography>
    </div>
    <div>
      <FirstStep />
    </div>
    <div>
      <SecondStep dataSourceId={dataSourceId} user={user} />
    </div>
    <div>
      <ThirdStep />
    </div>
  </Stack>
);

export default KubernetesIntegration;
