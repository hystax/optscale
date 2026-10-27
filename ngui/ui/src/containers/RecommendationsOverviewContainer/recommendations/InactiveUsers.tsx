import InactiveUsersModal from "components/SideModalManager/SideModals/recommendations/InactiveUsersModal";
import { AWS_IAM, GCP_IAM, NEBIUS_SERVICE } from "hooks/useRecommendationServices";
import { detectedAt, lastUsed, name, userLocation } from "utils/columns";
import { AWS_CNR, GCP_CNR, NEBIUS } from "utils/constants";
import BaseRecommendation, { CATEGORY } from "./BaseRecommendation";

const columns = [
  name({
    accessorKey: "user_name",
    captionAccessor: "user_id",
    headerDataTestId: "lbl_iu_name",
    enableTextCopy: true,
    defaultSort: "asc",
  }),
  userLocation({ headerDataTestId: "lbl_iu_location" }),
  lastUsed({ headerDataTestId: "lbl_iu_last_used" }),
  detectedAt({ headerDataTestId: "lbl_iu_detected_at" }),
];

class InactiveUsers extends BaseRecommendation {
  type = "inactive_users";

  name = "inactiveUsers";

  title = "inactiveUsersTitle";

  descriptionMessageId = "inactiveUsersDescription";

  get descriptionMessageValues() {
    const { days_threshold: daysThreshold } = this.options;

    return { daysThreshold };
  }

  emptyMessageId = "noInactiveUsers";

  services = [AWS_IAM, NEBIUS_SERVICE, GCP_IAM];

  appliedDataSources = [AWS_CNR, NEBIUS, GCP_CNR];

  categories = [CATEGORY.SECURITY];

  hasSettings = true;

  settingsSidemodalClass = InactiveUsersModal;

  dismissible = false;

  get previewItems() {
    return this.items.map((item) => [
      {
        key: `${item.user_name}-label`,
        value: item.user_name,
      },
    ]);
  }

  columns = columns;
}

export default InactiveUsers;
