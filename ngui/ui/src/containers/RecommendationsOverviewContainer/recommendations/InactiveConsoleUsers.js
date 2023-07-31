import InactiveConsoleUsersModal from "components/SideModalManager/SideModals/recommendations/InactiveConsoleUsersModal";
import { AWS_IAM } from "hooks/useRecommendationServices";
import { detectedAt, lastUsed, name, userLocation } from "utils/columns";
import BaseRecommendation, { CATEGORY_SECURITY } from "./BaseRecommendation";

const columns = [
  name({ accessorKey: "user_name", captionAccessor: "user_id", headerDataTestId: "lbl_iu_name", enableTextCopy: true }),
  userLocation({ headerDataTestId: "lbl_iu_location" }),
  lastUsed({ headerDataTestId: "lbl_iu_last_used" }),
  detectedAt({ headerDataTestId: "lbl_iu_detected_at" })
];

class InactiveConsoleUsers extends BaseRecommendation {
  type = "inactive_console_users";

  name = "inactiveConsoleUsers";

  title = "inactiveConsoleUsersTitle";

  descriptionMessageId = "inactiveConsoleUsersDescription";

  get descriptionMessageValues() {
    const { days_threshold: daysThreshold } = this.options;

    return { daysThreshold };
  }

  emptyMessageId = "noInactiveConsoleUsers";

  services = [AWS_IAM];

  categories = [CATEGORY_SECURITY];

  hasSettings = true;

  settingsSidemodalClass = InactiveConsoleUsersModal;

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

export default InactiveConsoleUsers;
