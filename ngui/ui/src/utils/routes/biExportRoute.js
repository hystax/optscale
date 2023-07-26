import { BI_EXPORT } from "urls";
import BaseRoute from "./baseRoute";

class BIExportRoute extends BaseRoute {
  page = "BIExport";

  link = BI_EXPORT;
}

export default new BIExportRoute();
