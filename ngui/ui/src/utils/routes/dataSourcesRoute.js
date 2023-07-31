import { CLOUD_ACCOUNTS } from "urls";
import BaseRoute from "./baseRoute";

class DataSourcesOverviewRoute extends BaseRoute {
  page = "CloudAccountsOverview";

  link = CLOUD_ACCOUNTS;
}

export default new DataSourcesOverviewRoute();
