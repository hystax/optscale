import { ORGANIZATION_OPTIONS } from "urls";
import BaseRoute from "./baseRoute";

class OrganizationOptionsRoute extends BaseRoute {
  page = "OrganizationOptions";

  link = ORGANIZATION_OPTIONS;
}

export default new OrganizationOptionsRoute();
