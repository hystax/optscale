import { CLOUD_ACCOUNT_CONNECT } from "urls";
import BaseRoute from "./baseRoute";

class CreateDataSourceRoute extends BaseRoute {
  page = "ConnectCloudAccount";

  link = CLOUD_ACCOUNT_CONNECT;
}

export default new CreateDataSourceRoute();
