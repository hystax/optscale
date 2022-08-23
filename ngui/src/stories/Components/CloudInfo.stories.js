import React from "react";
import CloudInfo from "components/CloudInfo";
import { AWS_CNR, AZURE_CNR, KUBERNETES_CNR } from "utils/constants";
import { ALIBABA_CNR } from "utils/constants";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/CloudInfo`
};

export const awsRootInfo = () => (
  <CloudInfo
    accountId="aws_root_id"
    lastImportAt={0}
    type={AWS_CNR}
    config={{
      linked: false
    }}
  />
);

export const awsLinkedInfo = () => (
  <CloudInfo
    accountId="aws_linked_id"
    lastImportAt={0}
    type={AWS_CNR}
    config={{
      linked: true
    }}
  />
);

export const azureInfo = () => (
  <CloudInfo
    accountId="azure_id"
    lastImportAt={0}
    type={AZURE_CNR}
    config={{
      tax_percent: 0
    }}
  />
);

export const k8sInfo = () => (
  <CloudInfo
    accountId="k8s_id"
    lastImportAt={0}
    type={KUBERNETES_CNR}
    config={{
      url: "https://127.0.0.1",
      port: "4433",
      user: "optscale"
    }}
  />
);

export const alibabaCloudInfo = () => <CloudInfo accountId="alibaba_cloud_id" lastImportAt={0} type={ALIBABA_CNR} />;
