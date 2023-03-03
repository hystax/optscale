import { QUOTA_AND_BUDGET } from "urls";
import BaseRoute from "./baseRoute";

class QuotaRoute extends BaseRoute {
  page = "OrganizationConstraint";

  link = QUOTA_AND_BUDGET;
}

export default new QuotaRoute();
