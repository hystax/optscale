import CloudOutlinedIcon from "@mui/icons-material/CloudOutlined";
import alibabaLogo from "assets/clouds/alibaba.svg";
import awsLogo from "assets/clouds/aws.svg";
import azureLogo from "assets/clouds/azure.svg";
import k8sLogo from "assets/clouds/k8s.svg";
import AlibabaLogoIcon from "icons/AlibabaLogoIcon";
import AwsLogoIcon from "icons/AwsLogoIcon";
import AzureLogoIcon from "icons/AzureLogoIcon";
import K8sLogoIcon from "icons/K8sLogoIcon";

import { AWS_CNR, AZURE_CNR, KUBERNETES_CNR, ALIBABA_CNR, ENVIRONMENT, CLOUD_ACCOUNT_TYPE } from "utils/constants";

const getSettings = (type) =>
  ({
    [AWS_CNR]: {
      icon: AwsLogoIcon,
      logo: awsLogo,
      dataTestIds: { img: "img_aws" },
      cloudInfoMessageId: "AWSAccountID",
      disconnectQuestionId: "disconnectAWSQuestion"
    },
    [AZURE_CNR]: {
      icon: AzureLogoIcon,
      logo: azureLogo,
      dataTestIds: { img: "img_azure" },
      cloudInfoMessageId: "azureSubscriptionID",
      disconnectQuestionId: "disconnectAzureQuestion"
    },
    [KUBERNETES_CNR]: {
      icon: K8sLogoIcon,
      logo: k8sLogo,
      dataTestIds: { img: "img_kubernetes", infoKey: "p_kubernetes_id", infoValue: "value_kubernetes_id" },
      cloudInfoMessageId: "kubernetesID",
      disconnectQuestionId: "disconnectKubernetesQuestion"
    },
    [ALIBABA_CNR]: {
      icon: AlibabaLogoIcon,
      logo: alibabaLogo,
      dataTestIds: { img: "img_alibaba", infoKey: "p_id", infoValue: "p_id_value" },
      cloudInfoMessageId: "alibabaAccountID",
      disconnectQuestionId: "disconnectAlibabaQuestion"
    },
    [ENVIRONMENT]: {
      icon: CloudOutlinedIcon,
      dataTestIds: { img: "img_environment" }
    }
  }[type] || {});

export const useDataSources = (type) => {
  const {
    icon = null,
    logo = null,
    cloudInfoMessageId = "",
    disconnectQuestionId = "disconnectQuestion",
    dataTestIds = {}
  } = getSettings(type);

  return {
    icon,
    logo,
    feType: CLOUD_ACCOUNT_TYPE[type] || null,
    cloudInfoMessageId,
    disconnectQuestionId,
    dataTestIds
  };
};
