import alibaba from "assets/marketplaces/alibaba.svg";
import aws from "assets/marketplaces/aws.svg";
import azure from "assets/marketplaces/azure.svg";
import gcp from "assets/marketplaces/gcp.svg";
import openstack from "assets/marketplaces/openstack.svg";
import vmware from "assets/marketplaces/vmware.svg";
import LandingPage from "components/LandingPage";
import {
  HYSTAX_CLOUD_MIGRATION,
  HYSTAX_CLOUD_MIGRATION_AWS,
  HYSTAX_CLOUD_MIGRATION_AZURE,
  HYSTAX_CLOUD_MIGRATION_GCP,
  HYSTAX_CLOUD_MIGRATION_VMWARE,
  HYSTAX_CLOUD_MIGRATION_ALIBABA,
  HYSTAX_CLOUD_MIGRATION_OPENSTACK
} from "urls";

const cloudItemsDefinition = [
  {
    href: HYSTAX_CLOUD_MIGRATION_AWS,
    src: aws,
    altMessageId: "aws"
  },
  {
    href: HYSTAX_CLOUD_MIGRATION_AZURE,
    src: azure,
    altMessageId: "azure"
  },
  {
    href: HYSTAX_CLOUD_MIGRATION_GCP,
    src: gcp,
    altMessageId: "gcp"
  },
  {
    href: HYSTAX_CLOUD_MIGRATION_VMWARE,
    src: vmware,
    altMessageId: "vmware"
  },
  {
    href: HYSTAX_CLOUD_MIGRATION_ALIBABA,
    src: alibaba,
    altMessageId: "alibaba"
  },
  {
    href: HYSTAX_CLOUD_MIGRATION_OPENSTACK,
    src: openstack,
    altMessageId: "openstack"
  }
];

const CloudMigration = () => (
  <LandingPage
    titleMessageId="cloudMigrationTitle"
    featureMessageId="cloudMigration"
    featureActionMessageId="migrate"
    featureUrl={HYSTAX_CLOUD_MIGRATION}
    cloudItemsDefinition={cloudItemsDefinition}
  />
);

export default CloudMigration;
