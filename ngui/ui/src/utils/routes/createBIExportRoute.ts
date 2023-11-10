import { CREATE_BI_EXPORT } from "urls";
import BaseRoute from "./baseRoute";

class CreateBIExportRoute extends BaseRoute {
  page = "CreateBIExport";

  link = CREATE_BI_EXPORT;
}

export default new CreateBIExportRoute();
