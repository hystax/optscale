import { CLOUD_ACCOUNT } from "urls";
import BaseRoute from "./baseRoute";

class DataSourceOverviewRoute extends BaseRoute {
  page = "CloudAccountDetails";

  link = CLOUD_ACCOUNT;
}

export default new DataSourceOverviewRoute();
