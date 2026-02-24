import { Stack } from "@mui/material";
import { FormattedMessage } from "react-intl";
import KeyValueLabel from "components/KeyValueLabel";
import RecommendationListItemResourceLabel from "components/RecommendationListItemResourceLabel";
import InsecurePortsModal from "components/SideModalManager/SideModals/recommendations/InsecurePortsModal";
import TextWithDataTestId from "components/TextWithDataTestId";
import {
  ALIBABA_ECS,
  ALIBABA_SLB,
  AWS_EC2_VPC,
  AZURE_NETWORK,
  GCP_COMPUTE_ENGINE,
  NEBIUS_SERVICE,
} from "hooks/useRecommendationServices";
import { detectedAt, openPorts, resource, resourceLocation } from "utils/columns";
import { AWS_CNR, AZURE_CNR, GCP_CNR, NEBIUS } from "utils/constants";
import BaseRecommendation, { CATEGORY } from "./BaseRecommendation";

const columns = [
  resource({
    headerDataTestId: "lbl_sg_resource",
  }),
  resourceLocation({
    headerDataTestId: "lbl_sg_location",
  }),
  {
    header: (
      <TextWithDataTestId dataTestId="lbl_sg_security_groups">
        <FormattedMessage id="securityGroup" />
      </TextWithDataTestId>
    ),
    accessorKey: "security_group_name",
  },
  openPorts({
    accessorKey: "insecure_ports",
    headerDataTestId: "lbl_sg_open_ports",
  }),
  detectedAt({ headerDataTestId: "lbl_sg_detected_at" }),
];

class InsecureSecurityGroups extends BaseRecommendation {
  type = "insecure_security_groups";

  name = "insecureSecurityGroups";

  title = "resourcesHaveInsecureSGSettingsTitle";

  descriptionMessageId = "insecureSecurityGroupsDescription";

  emptyMessageId = "noSGOpened";

  services = [AWS_EC2_VPC, AZURE_NETWORK, GCP_COMPUTE_ENGINE, NEBIUS_SERVICE, ALIBABA_ECS, ALIBABA_SLB];

  appliedDataSources = [AWS_CNR, AZURE_CNR, GCP_CNR, NEBIUS];

  categories = [CATEGORY.SECURITY];

  withExclusions = true;

  withInsecurePorts = true;

  hasSettings = true;

  settingsSidemodalClass = InsecurePortsModal;

  dismissible = false;

  static resourceDescriptionMessageId = "insecureSecurityGroupsResourceRecommendation";

  static getResourceDescriptionMessageValues(backendInfo) {
    const { security_group_name: groupName } = backendInfo;

    return { groupName };
  }

  get previewItems() {
    return this.items.map((item) => [
      {
        key: `${item.cloud_resource_id}-${item.security_group_name}`,
        value: (
          <Stack>
            <RecommendationListItemResourceLabel item={item} />
            <KeyValueLabel
              variant="caption"
              keyMessageId="securityGroup"
              value={item.security_group_name}
              isBoldValue={false}
            />
          </Stack>
        ),
      },
    ]);
  }

  columns = columns;
}

export default InsecureSecurityGroups;
