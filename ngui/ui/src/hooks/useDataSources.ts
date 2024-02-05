import CloudOutlinedIcon from "@mui/icons-material/CloudOutlined";
import alibabaLogo from "assets/clouds/alibaba.svg";
import awsLogo from "assets/clouds/aws.svg";
import azureLogo from "assets/clouds/azure.svg";
import databricksLogo from "assets/clouds/databricks.svg";
import gcpLogo from "assets/clouds/gcp.svg";
import k8sLogo from "assets/clouds/k8s.svg";
import nebiusLogo from "assets/clouds/nebius.svg";
import AlibabaLogoIcon from "icons/AlibabaLogoIcon";
import AwsLogoIcon from "icons/AwsLogoIcon";
import AzureLogoIcon from "icons/AzureLogoIcon";
import DatabricksLogoIcon from "icons/DatabricksLogoIcon";
import GcpLogoIcon from "icons/GcpLogoIcon";
import K8sLogoIcon from "icons/K8sLogoIcon";
import NebiusLogoIcon from "icons/NebiusLogoIcon";
import {
  AWS_CNR,
  AZURE_CNR,
  AZURE_TENANT,
  DATABRICKS,
  KUBERNETES_CNR,
  ALIBABA_CNR,
  ENVIRONMENT,
  GCP_CNR,
  CLOUD_ACCOUNT_TYPE,
  NEBIUS
} from "utils/constants";

export const getSettings = (type) =>
  ({
    [AWS_CNR]: {
      icon: AwsLogoIcon,
      logo: awsLogo,
      disconnectQuestionId: "disconnectAWSQuestion",
      cloudTypeMessageId: CLOUD_ACCOUNT_TYPE[AWS_CNR]
    },
    [AZURE_CNR]: {
      icon: AzureLogoIcon,
      logo: azureLogo,
      disconnectQuestionId: "disconnectAzureQuestion",
      cloudTypeMessageId: CLOUD_ACCOUNT_TYPE[AZURE_CNR]
    },
    [AZURE_TENANT]: {
      icon: AzureLogoIcon,
      logo: azureLogo,
      disconnectQuestionId: "disconnectAzureQuestion",
      cloudTypeMessageId: CLOUD_ACCOUNT_TYPE[AZURE_TENANT]
    },
    [DATABRICKS]: {
      icon: DatabricksLogoIcon,
      logo: databricksLogo,
      disconnectQuestionId: "disconnectAzureQuestion",
      cloudTypeMessageId: CLOUD_ACCOUNT_TYPE[DATABRICKS]
    },
    [KUBERNETES_CNR]: {
      icon: K8sLogoIcon,
      logo: k8sLogo,
      disconnectQuestionId: "disconnectKubernetesQuestion",
      cloudTypeMessageId: CLOUD_ACCOUNT_TYPE[KUBERNETES_CNR]
    },
    [ALIBABA_CNR]: {
      icon: AlibabaLogoIcon,
      logo: alibabaLogo,
      disconnectQuestionId: "disconnectAlibabaQuestion",
      cloudTypeMessageId: CLOUD_ACCOUNT_TYPE[ALIBABA_CNR]
    },
    [ENVIRONMENT]: {
      icon: CloudOutlinedIcon,
      cloudTypeMessageId: CLOUD_ACCOUNT_TYPE[ENVIRONMENT]
    },
    [GCP_CNR]: {
      icon: GcpLogoIcon,
      logo: gcpLogo,
      disconnectQuestionId: "disconnectGcpQuestion",
      cloudTypeMessageId: CLOUD_ACCOUNT_TYPE[GCP_CNR]
    },
    [NEBIUS]: {
      icon: NebiusLogoIcon,
      logo: nebiusLogo,
      disconnectQuestionId: "disconnectNebiusQuestion",
      cloudTypeMessageId: "nebius"
    }
  })[type] || {};

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
