import { POOL } from "urls";
import BaseRoute from "./baseRoute";

class OrganizationOverviewRoute extends BaseRoute {
  page = "OrganizationOverview";

  link = POOL;
}

export default new OrganizationOverviewRoute();
