import React from "react";
import alibaba from "assets/marketplaces/alibaba.svg";
import aws from "assets/marketplaces/aws.svg";
import azure from "assets/marketplaces/azure.svg";
import gcp from "assets/marketplaces/gcp.svg";
import openstack from "assets/marketplaces/openstack.svg";
import vmware from "assets/marketplaces/vmware.svg";
import LandingPage from "components/LandingPage";
import {
  HYSTAX_DISASTER_RECOVERY,
  HYSTAX_DISASTER_RECOVERY_AWS,
  HYSTAX_DISASTER_RECOVERY_AZURE,
  HYSTAX_DISASTER_RECOVERY_GCP,
  HYSTAX_DISASTER_RECOVERY_VMWARE,
  HYSTAX_DISASTER_RECOVERY_ALIBABA,
  HYSTAX_DISASTER_RECOVERY_OPENSTACK
} from "urls";

const cloudItemsDefinition = [
  {
    href: HYSTAX_DISASTER_RECOVERY_AWS,
    src: aws,
    altMessageId: "aws"
  },
  {
    href: HYSTAX_DISASTER_RECOVERY_AZURE,
    src: azure,
    altMessageId: "azure"
  },
  {
    href: HYSTAX_DISASTER_RECOVERY_GCP,
    src: gcp,
    altMessageId: "gcp"
  },
  {
    href: HYSTAX_DISASTER_RECOVERY_VMWARE,
    src: vmware,
    altMessageId: "vmware"
  },
  {
    href: HYSTAX_DISASTER_RECOVERY_ALIBABA,
    src: alibaba,
    altMessageId: "alibaba"
  },
  {
    href: HYSTAX_DISASTER_RECOVERY_OPENSTACK,
    src: openstack,
    altMessageId: "openstack"
  }
];

const DisasterRecovery = () => (
  <LandingPage
    titleMessageId="disasterRecoveryTitle"
    featureMessageId="disasterRecovery"
    featureActionMessageId="protect"
    featureUrl={HYSTAX_DISASTER_RECOVERY}
    cloudItemsDefinition={cloudItemsDefinition}
  />
);

export default DisasterRecovery;
