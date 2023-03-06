import CloudOutlinedIcon from "@mui/icons-material/CloudOutlined";
import alibabaLogo from "assets/clouds/alibaba.svg";
import awsLogo from "assets/clouds/aws.svg";
import azureLogo from "assets/clouds/azure.svg";
import gcpLogo from "assets/clouds/gcp.svg";
import k8sLogo from "assets/clouds/k8s.svg";
import AlibabaLogoIcon from "icons/AlibabaLogoIcon";
import AwsLogoIcon from "icons/AwsLogoIcon";
import AzureLogoIcon from "icons/AzureLogoIcon";
import GcpLogoIcon from "icons/GcpLogoIcon";
import K8sLogoIcon from "icons/K8sLogoIcon";
import { AWS_CNR, AZURE_CNR, KUBERNETES_CNR, ALIBABA_CNR, ENVIRONMENT, GCP_CNR } from "utils/constants";

const getSettings = (type) =>
  ({
    [AWS_CNR]: {
      icon: AwsLogoIcon,
      logo: awsLogo,
      cloudIdMessageId: "AWSAccountId",
      disconnectQuestionId: "disconnectAWSQuestion",
      cloudTypeMessageId: "aws"
    },
    [AZURE_CNR]: {
      icon: AzureLogoIcon,
      logo: azureLogo,
      cloudIdMessageId: "azureSubscriptionId",
      disconnectQuestionId: "disconnectAzureQuestion",
      cloudTypeMessageId: "azure"
    },
    [KUBERNETES_CNR]: {
      icon: K8sLogoIcon,
      logo: k8sLogo,
      cloudIdMessageId: "kubernetesId",
      disconnectQuestionId: "disconnectKubernetesQuestion",
      cloudTypeMessageId: "kubernetes"
    },
    [ALIBABA_CNR]: {
      icon: AlibabaLogoIcon,
      logo: alibabaLogo,
      cloudIdMessageId: "alibabaAccountId",
      disconnectQuestionId: "disconnectAlibabaQuestion",
      cloudTypeMessageId: "alibaba"
    },
    [ENVIRONMENT]: {
      icon: CloudOutlinedIcon,
      cloudTypeMessageId: "environment"
    },
    [GCP_CNR]: {
      icon: GcpLogoIcon,
      logo: gcpLogo,
      cloudIdMessageId: "GCPAccountId",
      disconnectQuestionId: "disconnectGcpQuestion",
      cloudTypeMessageId: "gcp"
    }
  }[type] || {});

export const useDataSources = (type) => {
  const {
    icon = null,
    logo = null,
    cloudIdMessageId = "",
    disconnectQuestionId = "disconnectQuestion",
    cloudTypeMessageId = ""
  } = getSettings(type);

  return {
    icon,
    logo,
    cloudIdMessageId,
    disconnectQuestionId,
    cloudTypeMessageId
  };
};
