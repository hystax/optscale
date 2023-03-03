import SecondaryLayout from "layouts/SecondaryLayout";
import { ORGANIZATIONS_OVERVIEW } from "urls";
import BaseRoute from "./baseRoute";

class OrganizationsOverviewRoute extends BaseRoute {
  page = "OrganizationsOverview";

  link = ORGANIZATIONS_OVERVIEW;

  layout = SecondaryLayout;
}

export default new OrganizationsOverviewRoute();
