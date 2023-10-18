import { lazy } from "react";
import { v4 as uuidv4 } from "uuid";
import MainLayout from "layouts/MainLayout";

class BaseRoute {
  key = uuidv4();

  link = "";

  page = "";

  layout = MainLayout;

  component = lazy(() =>
    // https://github.com/rollup/plugins/tree/master/packages/dynamic-import-vars#limitations
    import(`../../pages/${this.page}/index.js`)
  );
}

export default BaseRoute;
