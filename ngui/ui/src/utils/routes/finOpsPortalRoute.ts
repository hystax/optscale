import { FINOPS_PORTAL } from "urls";
import BaseRoute from "./baseRoute";

class FinOpsPortalRoute extends BaseRoute {
  page = "FinOpsPortal";

  link = FINOPS_PORTAL;
}

export default new FinOpsPortalRoute();
