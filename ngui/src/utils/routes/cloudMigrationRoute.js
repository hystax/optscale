import { CLOUD_MIGRATION } from "urls";
import BaseRoute from "./baseRoute";

class CloudMigrationRoute extends BaseRoute {
  page = "CloudMigration";

  link = CLOUD_MIGRATION;
}

export default new CloudMigrationRoute();
