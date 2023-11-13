import { FormattedMessage } from "react-intl";
import RecommendationListItemResourceLabel from "components/RecommendationListItemResourceLabel";
import InsecurePortsModal from "components/SideModalManager/SideModals/recommendations/InsecurePortsModal";
import TextWithDataTestId from "components/TextWithDataTestId";
import { AWS_EC2_VPC, AZURE_NETWORK, NEBIUS_SERVICE } from "hooks/useRecommendationServices";
import { detectedAt, openPorts, resource, resourceLocation } from "utils/columns";
import BaseRecommendation, { CATEGORY_SECURITY } from "./BaseRecommendation";

const columns = [
  resource({
    headerDataTestId: "lbl_sg_resource"
  }),
  resourceLocation({
    headerDataTestId: "lbl_sg_location"
  }),
  {
    header: (
      <TextWithDataTestId dataTestId="lbl_sg_security_groups">
        <FormattedMessage id="securityGroup" />
      </TextWithDataTestId>
    ),
    accessorKey: "security_group_name"
  },
  openPorts({
    accessorKey: "insecure_ports",
    headerDataTestId: "lbl_sg_open_ports"
  }),
  detectedAt({ headerDataTestId: "lbl_sg_detected_at" })
];

class InsecureSecurityGroups extends BaseRecommendation {
  type = "insecure_security_groups";

  name = "insecureSecurityGroups";

  title = "instancesHaveInsecureSGSettingsTitle";

  descriptionMessageId = "insecureSecurityGroupsDescription";

  emptyMessageId = "noSGOpened";

  services = [AWS_EC2_VPC, AZURE_NETWORK, NEBIUS_SERVICE];

  categories = [CATEGORY_SECURITY];

  withExclusions = true;

  withInsecurePorts = true;

  hasSettings = true;

  settingsSidemodalClass = InsecurePortsModal;

  dismissable = false;

  static resourceDescriptionMessageId = "insecureSecurityGroupsResourceRecommendation";

  static getResourceDescriptionMessageValues(backendInfo) {
    const { security_group_name: groupName } = backendInfo;

    return { groupName };
  }

  get previewItems() {
    return this.items.map((item) => [
      {
        key: `${item.cloud_resource_id}-label`,
        value: <RecommendationListItemResourceLabel item={item} />
      },
      {
        key: `${item.cloud_resource_id}-group-name`,
        value: item.security_group_name
      }
    ]);
  }

  columns = columns;
}

export default InsecureSecurityGroups;
