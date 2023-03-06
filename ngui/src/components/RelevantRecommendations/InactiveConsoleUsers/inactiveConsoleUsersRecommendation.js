import { detectedAt, lastUsed, name, userLocation } from "utils/columns";
import { RECOMMENDATION_INACTIVE_CONSOLE_USERS, INACTIVE_CONSOLE_USERS_TYPE } from "utils/constants";
import RecommendationFactory from "utils/recommendations";

class InactiveConsoleUsersRecommendation extends RecommendationFactory {
  type = RECOMMENDATION_INACTIVE_CONSOLE_USERS;

  moduleName = INACTIVE_CONSOLE_USERS_TYPE;

  withThresholds = true;

  messageId = "inactiveConsoleUsersTitle";

  configure() {
    return {
      type: this.type,
      moduleName: this.moduleName,
      withThresholds: this.withThresholds,
      descriptionMessageId: "inactiveConsoleUsersDescription",
      emptyMessageId: "noInactiveConsoleUsers",
      dataTestIds: {
        listTestId: "sp_inactive_console_users",
        textTestId: "p_inactive_console_users",
        buttonTestIds: ["btn_iu_download"]
      }
    };
  }

  static configureColumns() {
    return [
      name({ accessorKey: "user_name", captionAccessor: "user_id", headerDataTestId: "lbl_iu_name", enableTextCopy: true }),
      userLocation({ headerDataTestId: "lbl_iu_location" }),
      lastUsed({ headerDataTestId: "lbl_iu_last_used" }),
      detectedAt({ headerDataTestId: "lbl_iu_detected_at" })
    ];
  }
}

export default new InactiveConsoleUsersRecommendation();
