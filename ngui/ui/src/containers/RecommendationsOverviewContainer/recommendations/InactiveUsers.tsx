import InactiveUsersModal from "components/SideModalManager/SideModals/recommendations/InactiveUsersModal";
import { AWS_IAM, NEBIUS_SERVICE } from "hooks/useRecommendationServices";
import { detectedAt, lastUsed, name, userLocation } from "utils/columns";
import BaseRecommendation, { CATEGORY_SECURITY } from "./BaseRecommendation";

const columns = [
  name({ accessorKey: "user_name", captionAccessor: "user_id", headerDataTestId: "lbl_iu_name", enableTextCopy: true }),
  userLocation({ headerDataTestId: "lbl_iu_location" }),
  lastUsed({ headerDataTestId: "lbl_iu_last_used" }),
  detectedAt({ headerDataTestId: "lbl_iu_detected_at" })
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

  services = [AWS_IAM, NEBIUS_SERVICE];

  categories = [CATEGORY_SECURITY];

  hasSettings = true;

  settingsSidemodalClass = InactiveUsersModal;

  dismissable = false;

  get previewItems() {
    return this.items.map((item) => [
      {
        key: `${item.user_name}-label`,
        value: item.user_name
      }
    ]);
  }

  columns = columns;
}

export default InactiveUsers;
